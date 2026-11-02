"""Independent pandas calculation of every KPI, with the minimum group size rule.

This script reads only the raw tables (employees, absences, requisitions and the
dimensions). It does NOT read the fact_* files, so it is a genuine second
calculation to compare with the Power BI report and the agent answers.

Definitions (same as agent/knowledge/metric_definitions.md):
    headcount            employees employed after the last day of the period's last month
    hires                employees whose hire_date falls in the period
    voluntary_terminations / involuntary_terminations   counts of exits in the period
    turnover rate        terminations / average month-end headcount * 12 / months in period
    absence_rate         unplanned absence hours (Sick, Family, Personal) / scheduled hours
    avg_time_to_fill     mean days_to_fill of requisitions filled in the period
    group size           MIN(average month-end headcount, period-end headcount)
    suppression          group size below 5 employees, or fewer than 5 filled requisitions
                         for time to fill. Suppressed values are left blank.

Usage:
    python src/reference_kpis.py
Writes data/reference_kpis.csv (long), data/kpi_table.csv (wide, used by the flows),
agent/knowledge/kpi_facts.md (the same numbers as text lines, quarter and year only, for the
agent) and docs/reference_headlines.md (numbers quoted in the README).
The size of a suppressed group is never written to any output.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

MIN_GROUP_SIZE = 5
DAILY_HOURS = {"Full-time": 7.5, "Part-time": 4.5, "Contract": 7.5}
UNPLANNED_TYPES = ["Sick", "Family", "Personal"]
FAR = np.datetime64("2100-01-01")
DIMENSIONS = ["All", "Department", "Location", "Job level", "Department x Location"]
RATE_COLS = ["voluntary_turnover_rate", "involuntary_turnover_rate", "absence_rate"]


def load_inputs(data_dir):
    d = Path(data_dir)
    return dict(
        employees=pd.read_csv(d / "employees.csv", parse_dates=["hire_date", "termination_date"]),
        absences=pd.read_csv(d / "absences.csv", parse_dates=["date"]),
        requisitions=pd.read_csv(d / "requisitions.csv", parse_dates=["open_date", "filled_date"]),
        departments=pd.read_csv(d / "departments.csv"),
        locations=pd.read_csv(d / "locations.csv"),
        job_levels=pd.read_csv(d / "job_levels.csv"),
    )


class _Labeler:
    """Turns department, location and level keys into the member names of a dimension."""

    def __init__(self, departments, locations, job_levels):
        self.dept = dict(zip(departments.department_id, departments.department_name_en))
        self.loc = dict(zip(locations.location_id, locations.city_en))
        self.lvl = dict(zip(job_levels.job_level_id, job_levels.level_name_en))
        self.members = {
            "All": ["All"],
            "Department": list(self.dept.values()),
            "Location": list(self.loc.values()),
            "Job level": list(self.lvl.values()),
            "Department x Location": ["%s | %s" % (d, l) for d in self.dept.values() for l in self.loc.values()],
        }

    def labels(self, df, dim):
        if dim == "All":
            return pd.Series("All", index=df.index)
        if dim == "Department":
            return df.department_id.map(self.dept)
        if dim == "Location":
            return df.location_id.map(self.loc)
        if dim == "Job level":
            return df.job_level_id.map(self.lvl)
        return df.department_id.map(self.dept) + " | " + df.location_id.map(self.loc)

    def index(self, df, dim):
        pos = {m: i for i, m in enumerate(self.members[dim])}
        return self.labels(df, dim).map(pos).to_numpy()


def _group_sum(matrix, gidx, n_groups):
    out = np.zeros((n_groups, matrix.shape[1]))
    np.add.at(out, gidx, matrix)
    return out


def _periods(months):
    """List of (period_type, label, [month column positions], start, end)."""
    out = []
    for i, p in enumerate(months):
        out.append(("Month", str(p), [i], p.start_time, p.end_time.normalize()))
    for q, idx in pd.Series(range(len(months))).groupby([p.asfreq("Q") for p in months]):
        idx = list(idx)
        if len(idx) == 3:
            out.append(("Quarter", "%d-Q%d" % (q.year, q.quarter), idx,
                        months[idx[0]].start_time, months[idx[-1]].end_time.normalize()))
    for y, idx in pd.Series(range(len(months))).groupby([p.year for p in months]):
        idx = list(idx)
        label = str(y) if len(idx) == 12 else "%d YTD" % y
        out.append(("Year", label, idx, months[idx[0]].start_time, months[idx[-1]].end_time.normalize()))
    return out


def compute(employees, absences, requisitions, departments, locations, job_levels, start, as_of):
    """Returns (long, wide) DataFrames. start and as_of are dates (as_of is a month end)."""
    lab = _Labeler(departments, locations, job_levels)
    months = list(pd.period_range(pd.Timestamp(start), pd.Timestamp(as_of), freq="M"))
    ms = np.array([p.start_time for p in months], dtype="datetime64[D]")[None, :]
    me = np.minimum(np.array([p.end_time.normalize() for p in months], dtype="datetime64[D]"),
                    np.datetime64(pd.Timestamp(as_of), "D"))[None, :]

    emp = employees.reset_index(drop=True)
    hire = emp.hire_date.to_numpy().astype("datetime64[D]")[:, None]
    term = emp.termination_date.fillna(pd.Timestamp(FAR)).to_numpy().astype("datetime64[D]")[:, None]
    ttype = emp.termination_type.fillna("").to_numpy()[:, None]
    daily = emp.employment_type.map(DAILY_HOURS).to_numpy()[:, None]

    active_end = ((hire <= me) & (term > me)).astype(float)
    hired = ((hire >= ms) & (hire <= me)).astype(float)
    exited = (term >= ms) & (term <= me)
    vol = (exited & (ttype == "voluntary")).astype(float)
    invol = (exited & (ttype == "involuntary")).astype(float)

    first = np.maximum(hire, ms)
    last = np.minimum(term, me)
    valid = first <= last
    first = np.where(valid, first, ms)
    last = np.where(valid, last, ms - 1)  # busday_count of an empty range is 0
    sched = np.busday_count(first, last + 1).astype(float) * daily
    sched = np.where(valid, sched, 0.0)

    ab = absences[absences.type.isin(UNPLANNED_TYPES)].copy()
    ab["m"] = (ab.date.dt.year - months[0].year) * 12 + ab.date.dt.month - months[0].month
    ab = ab[(ab.m >= 0) & (ab.m < len(months))]
    pos = pd.Series(range(len(emp)), index=emp.employee_id)
    abs_hours = np.zeros_like(sched)
    np.add.at(abs_hours, (pos.reindex(ab.employee_id).to_numpy(), ab.m.to_numpy()), ab.hours.to_numpy())

    req = requisitions[requisitions.status == "Filled"].copy()
    req["m"] = (req.filled_date.dt.year - months[0].year) * 12 + req.filled_date.dt.month - months[0].month
    req = req[(req.m >= 0) & (req.m < len(months))]

    periods = _periods(months)
    latest = {}
    for ptype, label, *_ in periods:
        latest[ptype] = label  # periods are appended in chronological order within each type
    rows = []
    for dim in DIMENSIONS:
        members = lab.members[dim]
        ng = len(members)
        g = lab.index(emp, dim)
        gm = {name: _group_sum(mat, g, ng) for name, mat in
              [("hc", active_end), ("hire", hired), ("vol", vol), ("invol", invol),
               ("sched", sched), ("abs", abs_hours)]}
        rg = lab.index(req, dim)
        fill_n = _group_sum(np.ones((len(req), len(months))) * (req.m.to_numpy()[:, None] == np.arange(len(months))), rg, ng)
        fill_d = _group_sum((req.days_to_fill.to_numpy()[:, None] * (req.m.to_numpy()[:, None] == np.arange(len(months)))), rg, ng)
        for ptype, label, idx, pstart, pend in periods:
            n_months = len(idx)
            for gi, member in enumerate(members):
                hc_end = gm["hc"][gi, idx[-1]]
                avg_hc = gm["hc"][gi, idx].mean()
                size = min(hc_end, avg_hc)
                suppressed = dim != "All" and size < MIN_GROUP_SIZE
                vt, it = gm["vol"][gi, idx].sum(), gm["invol"][gi, idx].sum()
                hs = gm["sched"][gi, idx].sum()
                filled = fill_n[gi, idx].sum()
                ttf_suppressed = dim != "All" and filled < MIN_GROUP_SIZE
                rows.append(dict(
                    period_type=ptype, period=label, period_start=pstart.date().isoformat(),
                    period_end=pend.date().isoformat(), months_in_period=n_months,
                    is_latest="Yes" if latest[ptype] == label else "No",
                    dimension=dim, member=member,
                    group_size=None if suppressed else round(size, 1),  # never expose the size of a hidden group
                    suppressed="Yes" if suppressed else "No",
                    headcount=None if suppressed else int(hc_end),
                    hires=None if suppressed else int(gm["hire"][gi, idx].sum()),
                    voluntary_terminations=None if suppressed else int(vt),
                    involuntary_terminations=None if suppressed else int(it),
                    voluntary_turnover_rate=None if suppressed or avg_hc == 0 else round(vt / avg_hc * 12 / n_months, 6),
                    involuntary_turnover_rate=None if suppressed or avg_hc == 0 else round(it / avg_hc * 12 / n_months, 6),
                    absence_rate=None if suppressed or hs == 0 else round(gm["abs"][gi, idx].sum() / hs, 6),
                    filled_requisitions=int(filled),
                    ttf_suppressed="Yes" if ttf_suppressed else "No",
                    avg_time_to_fill_days=None if ttf_suppressed or filled == 0 else round(fill_d[gi, idx].sum() / filled, 2),
                ))
    wide = pd.DataFrame(rows)
    ids = ["period_type", "period", "dimension", "member", "group_size", "suppressed"]
    kpis = ["headcount", "hires", "voluntary_terminations", "involuntary_terminations",
            "voluntary_turnover_rate", "involuntary_turnover_rate", "absence_rate"]
    long = wide.melt(id_vars=ids, value_vars=kpis, var_name="kpi", value_name="value")
    ttf = wide[ids[:4] + ["filled_requisitions", "ttf_suppressed", "avg_time_to_fill_days"]].rename(
        columns={"filled_requisitions": "group_size", "ttf_suppressed": "suppressed",
                 "avg_time_to_fill_days": "value"})
    ttf["kpi"] = "avg_time_to_fill_days"
    ttf.loc[ttf.suppressed == "Yes", "group_size"] = np.nan
    long = pd.concat([long, ttf[ids + ["kpi", "value"]]], ignore_index=True)
    long["size_basis"] = np.where(long.kpi == "avg_time_to_fill_days", "filled_requisitions", "min(avg_headcount, headcount)")
    long["status"] = np.where(long.suppressed == "Yes", "Not enough data", "OK")
    return long, wide


def headline_markdown(wide):
    def pct(x):
        return "n/a" if pd.isna(x) else "%.1f%%" % (x * 100)

    q = wide[(wide.period_type == "Quarter") & (wide.is_latest == "Yes")]
    y = wide[(wide.period_type == "Year") & (wide.dimension == "All")]
    out = ["### Company level, by year", "",
           "| Period | Headcount (end) | Hires | Voluntary exits | Voluntary turnover (annualized) | Involuntary turnover (annualized) | Absence rate | Avg days to fill |",
           "|---|---|---|---|---|---|---|---|"]
    for _, r in y.iterrows():
        out.append("| %s | %d | %d | %d | %s | %s | %s | %.1f |" % (
            r.period, r.headcount, r.hires, r.voluntary_terminations,
            pct(r.voluntary_turnover_rate), pct(r.involuntary_turnover_rate),
            pct(r.absence_rate), r.avg_time_to_fill_days))
    label = q.period.iloc[0]
    out += ["", "### Latest quarter (%s) by department" % label, "",
            "| Department | Headcount | Voluntary turnover (annualized) | Absence rate |", "|---|---|---|---|"]
    for _, r in q[q.dimension == "Department"].sort_values("voluntary_turnover_rate", ascending=False).iterrows():
        out.append("| %s | %d | %s | %s |" % (r.member, r.headcount, pct(r.voluntary_turnover_rate), pct(r.absence_rate)))
    out += ["", "### Latest quarter (%s) by location" % label, "",
            "| Location | Headcount | Absence rate | Avg days to fill (filled in quarter) |", "|---|---|---|---|"]
    for _, r in q[q.dimension == "Location"].iterrows():
        out.append("| %s | %d | %s | %.1f |" % (r.member, r.headcount, pct(r.absence_rate), r.avg_time_to_fill_days))
    sup = q[(q.dimension == "Department x Location") & (q.suppressed == "Yes")]
    out += ["", "Department and location combinations suppressed in %s (fewer than 5 employees): %d of %d."
            % (label, len(sup), (q.dimension == "Department x Location").sum())]
    return "\n".join(out) + "\n"


def _pct(x, decimals=1):
    return "%.*f%%" % (decimals, x * 100)


def agent_facts_markdown(wide, departments, locations, job_levels):
    """The KPI table as self-contained text lines (quarters and years only) for the agent."""
    fr = {}
    fr.update(zip(departments.department_name_en, departments.department_name_fr))
    fr.update(zip(locations.city_en, locations.city_fr))
    fr.update(zip(job_levels.level_name_en, job_levels.level_name_fr))
    last_month = wide[wide.period_type == "Month"].period_end.max()
    latest_q = wide[(wide.period_type == "Quarter") & (wide.is_latest == "Yes")].period.iloc[0]
    out = [
        "# KPI facts for the HR Metrics Assistant",
        "",
        "Fictional company: Laurentian Financial Group. All data is synthetic.",
        "Generated by src/reference_kpis.py from the reference calculation. Do not edit by hand.",
        "Data ends on %s. The latest complete quarter is %s. Periods available: quarters (for example 2026-Q3)"
        " and years (2024, 2025, 2026 YTD which is January to September 2026). Months are not included." % (last_month, latest_q),
        "Rates are annualized (turnover) or shares of scheduled hours (absence). A line that says NOT ENOUGH DATA means the group"
        " is below the minimum group size of 5 employees and no value, count or size may be given.",
        "",
    ]
    sel = wide[wide.period_type.isin(["Quarter", "Year"])]
    for (ptype, period), block in sel.groupby(["period_type", "period"], sort=False):
        out += ["## %s (%s)" % (period, ptype), ""]
        for _, r in block.iterrows():
            names = r.member if r.dimension == "All" else " | ".join(
                "%s (%s)" % (m, fr.get(m, m)) if fr.get(m, m) != m else m for m in r.member.split(" | "))
            head = "%s, %s: %s" % (period, r.dimension, names)
            if r.suppressed == "Yes":
                out.append("- %s : NOT ENOUGH DATA (group below the minimum group size of 5). No values available." % head)
                continue
            ttf = ("average time to fill %.1f days (%d requisitions filled)" % (r.avg_time_to_fill_days, r.filled_requisitions)
                   if r.ttf_suppressed == "No" else "average time to fill: not enough data (fewer than 5 requisitions filled)")
            out.append(
                "- %s : headcount at end of period %d; hires %d; voluntary exits %d; involuntary exits %d; "
                "voluntary turnover (annualized) %s; involuntary turnover (annualized) %s; absence rate %s; %s."
                % (head, r.headcount, r.hires, r.voluntary_terminations, r.involuntary_terminations,
                   _pct(r.voluntary_turnover_rate), _pct(r.involuntary_turnover_rate), _pct(r.absence_rate), ttf))
        out.append("")
    return "\n".join(out)


def main():
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(root / "data"))
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--as-of", default="2026-09-30")
    args = ap.parse_args()
    long, wide = compute(**load_inputs(args.data_dir), start=args.start, as_of=args.as_of)
    d = Path(args.data_dir)
    long.to_csv(d / "reference_kpis.csv", index=False, lineterminator="\n", encoding="utf-8-sig")
    wide.to_csv(d / "kpi_table.csv", index=False, lineterminator="\n", encoding="utf-8-sig")
    inputs = load_inputs(args.data_dir)
    facts_dir = root / "agent" / "knowledge"
    facts_dir.mkdir(parents=True, exist_ok=True)
    (facts_dir / "kpi_facts.md").write_text(
        agent_facts_markdown(wide, inputs["departments"], inputs["locations"], inputs["job_levels"]),
        encoding="utf-8", newline="\n")
    md = headline_markdown(wide)
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "reference_headlines.md").write_text(md, encoding="utf-8")
    print(md)
    print("Wrote reference_kpis.csv (%d rows) and kpi_table.csv (%d rows)" % (len(long), len(wide)))


if __name__ == "__main__":
    main()
