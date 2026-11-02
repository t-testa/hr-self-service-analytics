"""Deterministic synthetic HR data generator for Laurentian Financial Group.

Laurentian Financial Group is a FICTIONAL company. Every record produced here is
synthetic. There are no real people, names or employer data.

Standard library only. Same seed gives byte-identical CSV files.

Usage (from the repo root):
    python src/generate_data.py
    python src/generate_data.py --out-dir data --seed 20261030

Planted patterns (so the analysis has something to find):
    1. Operations has much higher voluntary turnover than every other department.
    2. Absences peak in winter (flu season) and vacations peak in summer and December.
    3. Vancouver requisitions take about twice as long to fill as the others.
    4. A few department and location combinations have fewer than 5 employees,
       so the minimum group size rule has something to suppress.
    5. About 1 percent of employees have no language preference recorded
       (a deliberate data quality finding for the Data quality page).
"""

import argparse
import csv
import datetime as dt
import heapq
import random
from bisect import bisect_left, bisect_right
from pathlib import Path

SEED = 20261030
START = dt.date(2024, 1, 1)
AS_OF = dt.date(2026, 9, 30)  # last day of data
DATE_DIM_START = dt.date(2023, 1, 1)
DATE_DIM_END = dt.date(2026, 12, 31)
INITIAL_HEADCOUNT = 1500

# (id, name_en, name_fr, weight, annual voluntary rate, annual involuntary rate)
DEPARTMENTS = [
    ("D01", "Retail Banking", "Services bancaires aux particuliers", 0.25, 0.10, 0.020),
    ("D02", "Commercial Banking", "Services bancaires aux entreprises", 0.12, 0.08, 0.020),
    ("D03", "Wealth Management", "Gestion de patrimoine", 0.10, 0.07, 0.015),
    ("D04", "Operations", "Operations", 0.20, 0.27, 0.030),  # planted high turnover
    ("D05", "Technology", "Technologie", 0.14, 0.10, 0.020),
    ("D06", "Risk and Compliance", "Risques et conformite", 0.05, 0.07, 0.015),
    ("D07", "Finance", "Finance", 0.05, 0.07, 0.015),
    ("D08", "Human Resources", "Ressources humaines", 0.03, 0.08, 0.020),
    ("D09", "Marketing", "Marketing", 0.04, 0.10, 0.025),
    ("D10", "Legal", "Affaires juridiques", 0.02, 0.06, 0.010),
]
DEPT_FR_ACCENTS = {
    "Operations": "Opérations",
    "Risques et conformite": "Risques et conformité",
}

# (id, city_en, city_fr, province, weight, base mean days to fill)
LOCATIONS = [
    ("L01", "Montreal", "Montréal", "QC", 0.55, 36),
    ("L02", "Quebec City", "Québec", "QC", 0.15, 40),
    ("L03", "Toronto", "Toronto", "ON", 0.20, 42),
    ("L04", "Vancouver", "Vancouver", "BC", 0.10, 82),  # planted long time to fill
]

# (id, name_en, name_fr, order, weight)
JOB_LEVELS = [
    ("JL1", "Analyst / Associate", "Analyste / Associé", 1, 0.28),
    ("JL2", "Specialist", "Spécialiste", 2, 0.30),
    ("JL3", "Senior Specialist", "Spécialiste principal", 3, 0.24),
    ("JL4", "Manager", "Gestionnaire", 4, 0.12),
    ("JL5", "Director", "Directeur", 5, 0.045),
    ("JL6", "Vice-President", "Vice-président", 6, 0.015),
]

EMPLOYMENT_TYPES = [("Full-time", 0.88), ("Part-time", 0.07), ("Contract", 0.05)]
DAILY_HOURS = {"Full-time": 7.5, "Part-time": 4.5, "Contract": 7.5}

# Absence model: probability per weekday, exclusive outcomes.
SICK_BASE = 0.0195
FAMILY_BASE = 0.0020
PERSONAL_BASE = 0.0030
VACATION_BASE = 0.0350
SICK_SEASON = {1: 1.9, 2: 1.8, 3: 1.1, 4: 0.9, 5: 0.8, 6: 0.7, 7: 0.6,
               8: 0.6, 9: 0.9, 10: 1.0, 11: 1.3, 12: 1.5}
VACATION_SEASON = {1: 0.5, 2: 0.6, 3: 0.8, 4: 0.9, 5: 1.0, 6: 1.4, 7: 2.6,
                   8: 2.6, 9: 0.9, 10: 0.8, 11: 0.7, 12: 2.3}
SICK_DEPT_MULT = {"D04": 1.2}
SICK_LOC_MULT = {"L02": 1.15}

MONTH_EN = ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]
MONTH_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
DAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# (table file, [(column, type, description)])
DICTIONARY = {
    "employees": [
        ("employee_id", "text", "Synthetic employee key, for example E00001. Not a real identifier."),
        ("hire_date", "date", "First day of work. ISO format YYYY-MM-DD."),
        ("termination_date", "date", "Last day of work. Blank when the employee is still active at the end of the data."),
        ("termination_type", "text", "voluntary (employee chose to leave) or involuntary (employer decision). Blank when active."),
        ("department_id", "text", "Key to departments.department_id."),
        ("job_level_id", "text", "Key to job_levels.job_level_id."),
        ("location_id", "text", "Key to locations.location_id."),
        ("manager_id", "text", "employee_id of the manager. Blank for Vice-Presidents, who sit at the top of this fictional hierarchy."),
        ("employment_type", "text", "Full-time, Part-time or Contract. Drives scheduled hours per day (7.5, 4.5, 7.5)."),
        ("language_preference", "text", "FR or EN. Blank when not recorded (about 1 percent of employees, a planted data quality issue)."),
    ],
    "departments": [
        ("department_id", "text", "Department key, D01 to D10."),
        ("department_name_en", "text", "Department name in English."),
        ("department_name_fr", "text", "Department name in French."),
    ],
    "locations": [
        ("location_id", "text", "Location key, L01 to L04."),
        ("city_en", "text", "City name in English."),
        ("city_fr", "text", "City name in French."),
        ("province", "text", "Two letter province code."),
    ],
    "job_levels": [
        ("job_level_id", "text", "Job level key, JL1 to JL6."),
        ("level_name_en", "text", "Level name in English."),
        ("level_name_fr", "text", "Level name in French."),
        ("level_order", "integer", "1 is the most junior level, 6 the most senior. Use for sorting."),
    ],
    "dates": [
        ("date_key", "integer", "Date as YYYYMMDD."),
        ("date", "date", "Calendar date."),
        ("year", "integer", "Calendar year."),
        ("quarter_number", "integer", "Quarter 1 to 4."),
        ("quarter_label", "text", "Year and quarter, for example 2026-Q3."),
        ("month_number", "integer", "Month 1 to 12."),
        ("year_month", "text", "Year and month, for example 2026-09. Sorts correctly as text."),
        ("month_name_en", "text", "Month name in English."),
        ("month_name_fr", "text", "Month name in French."),
        ("day_name_en", "text", "Weekday name in English."),
        ("is_weekday", "integer", "1 for Monday to Friday, else 0. Statutory holidays are not modelled."),
        ("month_end_date", "date", "Last calendar day of the month of this date."),
        ("is_month_end", "integer", "1 when this date is the last day of its month."),
        ("is_in_data_range", "integer", "1 when the date is on or before the as-of date of the data (2026-09-30)."),
    ],
    "absences": [
        ("employee_id", "text", "Key to employees.employee_id."),
        ("date", "date", "Day of the absence. One row per employee per day."),
        ("type", "text", "Sick, Family, Personal or Vacation."),
        ("hours", "decimal", "Hours absent that day. A full day is the employee's daily scheduled hours, a half day is half of it."),
    ],
    "requisitions": [
        ("requisition_id", "text", "Requisition key, for example R00001."),
        ("open_date", "date", "Date the role was opened."),
        ("department_id", "text", "Key to departments.department_id."),
        ("location_id", "text", "Key to locations.location_id."),
        ("job_level_id", "text", "Key to job_levels.job_level_id."),
        ("employment_type", "text", "Full-time, Part-time or Contract."),
        ("reason", "text", "Backfill (replaces a departure) or Growth (new role)."),
        ("status", "text", "Filled, Open (not yet filled at the as-of date) or Cancelled."),
        ("filled_date", "date", "Start date of the person hired. Blank unless status is Filled."),
        ("days_to_fill", "integer", "Calendar days from open_date to filled_date. Blank unless status is Filled."),
    ],
    "fact_headcount_snapshot": [
        ("snapshot_date", "date", "Last day of the month. One row per employee who was employed at any point in that month."),
        ("employee_id", "text", "Key to employees.employee_id. Hidden in the Power BI model, never shown in visuals."),
        ("department_id", "text", "Key to departments.department_id."),
        ("location_id", "text", "Key to locations.location_id."),
        ("job_level_id", "text", "Key to job_levels.job_level_id."),
        ("employment_type", "text", "Full-time, Part-time or Contract."),
        ("active_at_month_end", "integer", "1 if still employed after the last day of the month, else 0. Headcount is the sum of this column."),
        ("hired_in_month", "integer", "1 if the hire_date falls in this month. Hires is the sum of this column."),
        ("scheduled_hours", "decimal", "Weekday count while employed in the month times daily hours. Denominator of the absence rate."),
    ],
    "fact_terminations": [
        ("employee_id", "text", "Key to employees.employee_id. Hidden in the Power BI model."),
        ("termination_date", "date", "Last day of work."),
        ("termination_type", "text", "voluntary or involuntary."),
        ("department_id", "text", "Key to departments.department_id."),
        ("location_id", "text", "Key to locations.location_id."),
        ("job_level_id", "text", "Key to job_levels.job_level_id."),
        ("employment_type", "text", "Full-time, Part-time or Contract."),
        ("tenure_months", "integer", "Whole months between hire_date and termination_date."),
    ],
    "fact_absences": [
        ("employee_id", "text", "Key to employees.employee_id. Hidden in the Power BI model."),
        ("date", "date", "Day of the absence."),
        ("type", "text", "Sick, Family, Personal or Vacation."),
        ("hours", "decimal", "Hours absent that day."),
        ("department_id", "text", "Key to departments.department_id."),
        ("location_id", "text", "Key to locations.location_id."),
        ("job_level_id", "text", "Key to job_levels.job_level_id."),
        ("counts_in_absence_rate", "integer", "1 for Sick, Family and Personal, 0 for Vacation. Vacation is planned leave and is not an absence for the rate."),
    ],
}


def weekdays_between(a, b):
    """Number of Monday to Friday days from a to b inclusive."""
    if b < a:
        return 0
    n = (b - a).days + 1
    full, rest = divmod(n, 7)
    count = full * 5
    for i in range(rest):
        if (a + dt.timedelta(days=full * 7 + i)).weekday() < 5:
            count += 1
    return count


def month_bounds(year, month):
    first = dt.date(year, month, 1)
    nxt = dt.date(year + (month == 12), month % 12 + 1, 1)
    return first, nxt - dt.timedelta(days=1)


def months_in_range(start, end):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


class Generator:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.employees = []
        self.requisitions = []
        self.active = []
        self.pending = []  # heap of (hire_date, counter, requisition)
        self._counter = 0
        self._next_emp = 1
        self.dept_ids = [d[0] for d in DEPARTMENTS]
        self.dept_w = [d[3] for d in DEPARTMENTS]
        self.dept_vol = {d[0]: d[4] for d in DEPARTMENTS}
        self.dept_invol = {d[0]: d[5] for d in DEPARTMENTS}
        self.loc_ids = [x[0] for x in LOCATIONS]
        self.loc_w = [x[4] for x in LOCATIONS]
        self.loc_ttf = {x[0]: x[5] for x in LOCATIONS}
        self.level_ids = [x[0] for x in JOB_LEVELS]
        self.level_w = [x[4] for x in JOB_LEVELS]
        self.mgr_pool = {}

    # ----- helpers -----
    def pick(self, ids, weights):
        return self.rng.choices(ids, weights)[0]

    def pick_language(self, loc):
        fr_share = {"L01": 0.78, "L02": 0.92, "L03": 0.12, "L04": 0.08}[loc]
        if self.rng.random() < 0.01:
            return ""
        return "FR" if self.rng.random() < fr_share else "EN"

    def new_employee(self, hire_date, dept, loc, level, etype):
        emp = {
            "employee_id": "E%05d" % self._next_emp,
            "hire_date": hire_date,
            "termination_date": None,
            "termination_type": "",
            "department_id": dept,
            "job_level_id": level,
            "location_id": loc,
            "manager_id": "",
            "employment_type": etype,
            "language_preference": self.pick_language(loc),
        }
        self._next_emp += 1
        self.employees.append(emp)
        return emp

    def pick_manager(self, emp):
        own = int(emp["job_level_id"][2:])
        dept = emp["department_id"]
        for lvl in range(own + 1, 7):
            pool = self.mgr_pool.get((dept, lvl))
            if pool:
                return self.rng.choice(pool)
        for lvl in range(own + 1, 7):
            pool = [e for (d, l), es in self.mgr_pool.items() if l == lvl for e in es]
            if pool:
                return self.rng.choice(sorted(pool))
        return ""

    def draw_days_to_fill(self, loc, level):
        lvl = int(level[2:])
        mean = self.loc_ttf[loc] + 6 * max(0, lvl - 2)
        return max(10, int(round(self.rng.gauss(mean, mean * 0.22))))

    def open_requisition(self, open_date, dept, loc, level, etype, reason, floor_fill=None):
        req = {
            "open_date": open_date, "department_id": dept, "location_id": loc,
            "job_level_id": level, "employment_type": etype, "reason": reason,
            "status": "Open", "filled_date": None, "days_to_fill": None,
        }
        self.requisitions.append(req)
        if self.rng.random() < 0.05:
            req["status"] = "Cancelled"
            return
        fill = open_date + dt.timedelta(days=self.draw_days_to_fill(loc, level))
        if floor_fill is not None and fill < floor_fill:
            fill = floor_fill + dt.timedelta(days=self.rng.randint(0, 20))
        if fill <= AS_OF:
            req["status"] = "Filled"
            req["filled_date"] = fill
            req["days_to_fill"] = (fill - open_date).days
            self._counter += 1
            heapq.heappush(self.pending, (fill, self._counter, req))

    # ----- simulation -----
    def build_initial(self):
        for _ in range(INITIAL_HEADCOUNT):
            tenure = min(int(self.rng.expovariate(1 / 2000)), 7000) + 1
            hire = dt.date(2023, 12, 31) - dt.timedelta(days=tenure)
            self.new_employee(
                hire,
                self.pick(self.dept_ids, self.dept_w),
                self.pick(self.loc_ids, self.loc_w),
                self.pick(self.level_ids, self.level_w),
                self.pick([t for t, _ in EMPLOYMENT_TYPES], [w for _, w in EMPLOYMENT_TYPES]),
            )
        for emp in self.employees:
            lvl = int(emp["job_level_id"][2:])
            if lvl >= 4:
                self.mgr_pool.setdefault((emp["department_id"], lvl), []).append(emp["employee_id"])
        for emp in self.employees:
            emp["manager_id"] = self.pick_manager(emp)
        self.active = list(self.employees)

    def seed_pipeline(self):
        """Requisitions opened in Nov and Dec 2023 that fill in early 2024."""
        for _ in range(30):
            open_date = dt.date(2023, 11, 1) + dt.timedelta(days=self.rng.randint(0, 60))
            self.open_requisition(
                open_date,
                self.pick(self.dept_ids, self.dept_w),
                self.pick(self.loc_ids, self.loc_w),
                self.pick(self.level_ids, self.level_w),
                self.pick([t for t, _ in EMPLOYMENT_TYPES], [w for _, w in EMPLOYMENT_TYPES]),
                "Backfill", floor_fill=START,
            )

    def run(self):
        self.build_initial()
        self.seed_pipeline()
        year_factor = {2024: 1.0, 2025: 0.95, 2026: 1.05}
        for y, m in months_in_range(START, AS_OF):
            ms, me = month_bounds(y, m)
            me = min(me, AS_OF)
            while self.pending and self.pending[0][0] <= me:
                hire_date, _, req = heapq.heappop(self.pending)
                emp = self.new_employee(hire_date, req["department_id"], req["location_id"],
                                        req["job_level_id"], req["employment_type"])
                emp["manager_id"] = self.pick_manager(emp)
                self.active.append(emp)
            still_active = []
            span = (me - ms).days
            for emp in self.active:
                if emp["hire_date"] >= ms:
                    still_active.append(emp)  # no exit in the month of arrival
                    continue
                tenure_days = (ms - emp["hire_date"]).days
                bump = 1.3 if tenure_days < 365 else 1.0
                pv = 1 - (1 - self.dept_vol[emp["department_id"]] * year_factor[y] * bump) ** (1 / 12)
                pi = 1 - (1 - self.dept_invol[emp["department_id"]]) ** (1 / 12)
                u = self.rng.random()
                if u < pv:
                    ttype = "voluntary"
                elif u < pv + pi:
                    ttype = "involuntary"
                else:
                    still_active.append(emp)
                    continue
                day = ms + dt.timedelta(days=self.rng.randint(0, span))
                day = max(day, emp["hire_date"] + dt.timedelta(days=1))
                day = min(day, me)
                emp["termination_date"] = day
                emp["termination_type"] = ttype
                if self.rng.random() < 0.93:
                    open_date = day + dt.timedelta(days=self.rng.randint(0, 21))
                    if open_date <= AS_OF:
                        self.open_requisition(open_date, emp["department_id"], emp["location_id"],
                                              emp["job_level_id"], emp["employment_type"], "Backfill")
            self.active = still_active
            growth = len(self.active) * 0.002
            n_growth = int(growth) + (1 if self.rng.random() < growth - int(growth) else 0)
            for _ in range(n_growth):
                open_date = ms + dt.timedelta(days=self.rng.randint(0, span))
                self.open_requisition(
                    open_date,
                    self.pick(self.dept_ids, self.dept_w),
                    self.pick(self.loc_ids, self.loc_w),
                    self.pick(self.level_ids, self.level_w),
                    self.pick([t for t, _ in EMPLOYMENT_TYPES], [w for _, w in EMPLOYMENT_TYPES]),
                    "Growth",
                )
        self.requisitions.sort(key=lambda r: r["open_date"])  # stable sort keeps ties deterministic
        for i, req in enumerate(self.requisitions, start=1):
            req["requisition_id"] = "R%05d" % i

    def absences(self):
        wd = []
        d = START
        while d <= AS_OF:
            if d.weekday() < 5:
                wd.append(d)
            d += dt.timedelta(days=1)
        month_of = [x.month for x in wd]
        rng = self.rng
        rows = []
        for emp in self.employees:
            start = max(emp["hire_date"], START)
            end = min(emp["termination_date"] or AS_OF, AS_OF)
            lo, hi = bisect_left(wd, start), bisect_right(wd, end)
            if lo >= hi:
                continue
            mult = SICK_DEPT_MULT.get(emp["department_id"], 1.0) * SICK_LOC_MULT.get(emp["location_id"], 1.0)
            daily = DAILY_HOURS[emp["employment_type"]]
            thresholds = {}
            for m in range(1, 13):
                t1 = SICK_BASE * SICK_SEASON[m] * mult
                t2 = t1 + FAMILY_BASE
                t3 = t2 + PERSONAL_BASE
                t4 = t3 + VACATION_BASE * VACATION_SEASON[m]
                thresholds[m] = (t1, t2, t3, t4)
            for i in range(lo, hi):
                r = rng.random()
                t1, t2, t3, t4 = thresholds[month_of[i]]
                if r >= t4:
                    continue
                kind = "Sick" if r < t1 else "Family" if r < t2 else "Personal" if r < t3 else "Vacation"
                hours = daily if rng.random() > 0.15 else daily / 2
                rows.append((wd[i], emp["employee_id"], kind, hours))
        rows.sort(key=lambda x: (x[0], x[1]))
        return rows


def date_dimension():
    rows = []
    d = DATE_DIM_START
    while d <= DATE_DIM_END:
        _, mend = month_bounds(d.year, d.month)
        q = (d.month - 1) // 3 + 1
        rows.append([
            d.strftime("%Y%m%d"), d.isoformat(), d.year, q, "%d-Q%d" % (d.year, q), d.month,
            "%d-%02d" % (d.year, d.month), MONTH_EN[d.month - 1], MONTH_FR[d.month - 1],
            DAY_EN[d.weekday()], int(d.weekday() < 5), mend.isoformat(), int(d == mend),
            int(d <= AS_OF),
        ])
        d += dt.timedelta(days=1)
    return rows


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def fmt_hours(h):
    return ("%.2f" % h).rstrip("0").rstrip(".")


def generate(out_dir, seed=SEED):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    g = Generator(seed)
    g.run()
    absences = g.absences()
    iso = lambda d: d.isoformat() if d else ""
    emp_by_id = {e["employee_id"]: e for e in g.employees}

    def cols(table):
        return [c[0] for c in DICTIONARY[table]]

    write_csv(out / "departments.csv", cols("departments"),
              [[d[0], d[1], DEPT_FR_ACCENTS.get(d[2], d[2])] for d in DEPARTMENTS])
    write_csv(out / "locations.csv", cols("locations"), [[x[0], x[1], x[2], x[3]] for x in LOCATIONS])
    write_csv(out / "job_levels.csv", cols("job_levels"), [[x[0], x[1], x[2], x[3]] for x in JOB_LEVELS])
    write_csv(out / "dates.csv", cols("dates"), date_dimension())

    write_csv(out / "employees.csv", cols("employees"), [
        [e["employee_id"], iso(e["hire_date"]), iso(e["termination_date"]), e["termination_type"],
         e["department_id"], e["job_level_id"], e["location_id"], e["manager_id"],
         e["employment_type"], e["language_preference"]] for e in g.employees])

    write_csv(out / "absences.csv", cols("absences"),
              [[eid, iso(d), kind, fmt_hours(h)] for d, eid, kind, h in absences])

    write_csv(out / "requisitions.csv", cols("requisitions"), [
        [r["requisition_id"], iso(r["open_date"]), r["department_id"], r["location_id"],
         r["job_level_id"], r["employment_type"], r["reason"], r["status"],
         iso(r["filled_date"]), "" if r["days_to_fill"] is None else r["days_to_fill"]]
        for r in g.requisitions])

    snap = []
    for y, m in months_in_range(START, AS_OF):
        ms, me = month_bounds(y, m)
        me = min(me, AS_OF)
        for e in g.employees:
            term = e["termination_date"]
            if e["hire_date"] > me or (term and term < ms):
                continue
            first = max(e["hire_date"], ms)
            last = min(term, me) if term else me
            hours = weekdays_between(first, last) * DAILY_HOURS[e["employment_type"]]
            snap.append([
                me.isoformat(), e["employee_id"], e["department_id"], e["location_id"],
                e["job_level_id"], e["employment_type"],
                int(not term or term > me), int(ms <= e["hire_date"] <= me), fmt_hours(hours),
            ])
    write_csv(out / "fact_headcount_snapshot.csv", cols("fact_headcount_snapshot"), snap)

    terms = []
    for e in g.employees:
        if e["termination_date"]:
            h, t = e["hire_date"], e["termination_date"]
            months = (t.year - h.year) * 12 + t.month - h.month - (t.day < h.day)
            terms.append([e["employee_id"], iso(t), e["termination_type"], e["department_id"],
                          e["location_id"], e["job_level_id"], e["employment_type"], months])
    terms.sort(key=lambda r: (r[1], r[0]))
    write_csv(out / "fact_terminations.csv", cols("fact_terminations"), terms)

    write_csv(out / "fact_absences.csv", cols("fact_absences"), [
        [eid, iso(d), kind, fmt_hours(h), emp_by_id[eid]["department_id"],
         emp_by_id[eid]["location_id"], emp_by_id[eid]["job_level_id"], int(kind != "Vacation")]
        for d, eid, kind, h in absences])

    dd_rows = [[t, c, ty, desc] for t, items in DICTIONARY.items() for c, ty, desc in items]
    write_csv(out / "data_dictionary.csv", ["table", "column", "data_type", "description"], dd_rows)
    return {"employees": len(g.employees), "absences": len(absences),
            "requisitions": len(g.requisitions), "terminations": len(terms),
            "snapshot_rows": len(snap)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent.parent / "data"))
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    summary = generate(args.out_dir, args.seed)
    print("Synthetic data written to", args.out_dir)
    for k, v in summary.items():
        print("  %-14s %d" % (k, v))


if __name__ == "__main__":
    main()
