import hashlib
from pathlib import Path

import pandas as pd
import pytest

import generate_data as gd


def digest(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(folder).glob("*.csv"))}


def read(data_dir, name):
    return pd.read_csv(Path(data_dir) / (name + ".csv"))


def test_same_seed_gives_identical_files(data_dir, tmp_path):
    gd.generate(tmp_path)
    assert digest(tmp_path) == digest(data_dir)


def test_different_seed_changes_data(data_dir, tmp_path):
    gd.generate(tmp_path, seed=7)
    assert digest(tmp_path)["employees.csv"] != digest(data_dir)["employees.csv"]


def test_every_column_is_in_the_data_dictionary(data_dir):
    dictionary = read(data_dir, "data_dictionary")
    assert dictionary.description.str.len().min() > 10
    for table, items in gd.DICTIONARY.items():
        frame = read(data_dir, table)
        assert list(frame.columns) == [c[0] for c in items], table
        listed = dictionary[dictionary.table == table].column.tolist()
        assert listed == list(frame.columns)


def test_keys_are_unique(data_dir):
    assert read(data_dir, "employees").employee_id.is_unique
    assert read(data_dir, "requisitions").requisition_id.is_unique
    assert not read(data_dir, "absences").duplicated(["employee_id", "date"]).any()


def test_referential_integrity(data_dir):
    emp = read(data_dir, "employees")
    dept = set(read(data_dir, "departments").department_id)
    loc = set(read(data_dir, "locations").location_id)
    lvl = set(read(data_dir, "job_levels").job_level_id)
    ids = set(emp.employee_id)
    for frame in (emp, read(data_dir, "requisitions"), read(data_dir, "fact_terminations"),
                  read(data_dir, "fact_absences"), read(data_dir, "fact_headcount_snapshot")):
        assert set(frame.department_id) <= dept
        assert set(frame.location_id) <= loc
        assert set(frame.job_level_id) <= lvl
    assert set(emp.manager_id.dropna()) <= ids
    assert set(read(data_dir, "absences").employee_id) <= ids
    assert set(read(data_dir, "fact_headcount_snapshot").employee_id) <= ids
    assert set(read(data_dir, "fact_terminations").employee_id) <= ids
    dates = set(read(data_dir, "dates").date)
    assert set(read(data_dir, "absences").date) <= dates
    assert set(read(data_dir, "requisitions").open_date) <= dates
    assert set(read(data_dir, "requisitions").filled_date.dropna()) <= dates


def test_employee_dates_and_termination_rules(data_dir):
    emp = pd.read_csv(Path(data_dir) / "employees.csv", parse_dates=["hire_date", "termination_date"])
    termed = emp[emp.termination_date.notna()]
    assert (termed.termination_date > termed.hire_date).all()
    assert set(termed.termination_type) == {"voluntary", "involuntary"}
    assert emp[emp.termination_date.isna()].termination_type.isna().all()
    assert emp.termination_date.max() <= pd.Timestamp(gd.AS_OF)
    assert (emp.manager_id != emp.employee_id).all()


def test_absences_fall_inside_employment_and_daily_hours(data_dir):
    emp = pd.read_csv(Path(data_dir) / "employees.csv", parse_dates=["hire_date", "termination_date"])
    ab = pd.read_csv(Path(data_dir) / "absences.csv", parse_dates=["date"]).merge(emp, on="employee_id")
    assert (ab.date >= ab.hire_date).all()
    assert (ab.termination_date.isna() | (ab.date <= ab.termination_date)).all()
    assert (ab.date.dt.weekday < 5).all()
    daily = ab.employment_type.map(gd.DAILY_HOURS)
    assert (ab.hours <= daily).all() and (ab.hours > 0).all()


def test_requisition_fields_are_consistent(data_dir):
    req = pd.read_csv(Path(data_dir) / "requisitions.csv", parse_dates=["open_date", "filled_date"])
    filled = req[req.status == "Filled"]
    assert ((filled.filled_date - filled.open_date).dt.days == filled.days_to_fill).all()
    assert req[req.status != "Filled"].days_to_fill.isna().all()
    assert (filled.filled_date <= pd.Timestamp(gd.AS_OF)).all()


def test_facts_match_employees(data_dir):
    emp = read(data_dir, "employees")
    snap = read(data_dir, "fact_headcount_snapshot")
    last = snap[snap.snapshot_date == snap.snapshot_date.max()]
    assert last.active_at_month_end.sum() == emp.termination_date.isna().sum()
    assert len(read(data_dir, "fact_terminations")) == emp.termination_date.notna().sum()
    assert len(read(data_dir, "fact_absences")) == len(read(data_dir, "absences"))
    assert read(data_dir, "fact_absences").query("type == 'Vacation'").counts_in_absence_rate.eq(0).all()


def test_planted_operations_has_highest_voluntary_turnover(data_dir):
    snap = read(data_dir, "fact_headcount_snapshot")
    terms = read(data_dir, "fact_terminations").query("termination_type == 'voluntary'")
    avg_hc = snap.groupby(["snapshot_date", "department_id"]).active_at_month_end.sum().groupby("department_id").mean()
    rate = terms.groupby("department_id").size() / avg_hc
    ranked = rate.sort_values(ascending=False)
    assert ranked.index[0] == "D04"
    assert ranked.iloc[0] > 2 * ranked.iloc[1] / 1.2  # clearly above every other department


def test_planted_vancouver_is_slowest_to_fill(data_dir):
    req = read(data_dir, "requisitions").query("status == 'Filled'")
    means = req.groupby("location_id").days_to_fill.mean()
    others = means.drop("L04").max()
    assert means["L04"] > 1.6 * others


def test_planted_seasonal_absence_peak(data_dir):
    snap = read(data_dir, "fact_headcount_snapshot")
    snap["month"] = snap.snapshot_date.str[5:7].astype(int)
    ab = read(data_dir, "fact_absences").query("counts_in_absence_rate == 1")
    ab["month"] = ab.date.str[5:7].astype(int)
    rate = ab.groupby("month").hours.sum() / snap.groupby("month").scheduled_hours.sum()
    assert rate[[1, 2]].mean() > 1.5 * rate[[6, 7, 8]].mean()


def test_planted_small_groups_exist_for_the_privacy_rule(data_dir):
    emp = read(data_dir, "employees")
    active = emp[emp.termination_date.isna()]
    sizes = active.groupby(["department_id", "location_id"]).size().reindex(
        pd.MultiIndex.from_product([sorted(set(emp.department_id)), sorted(set(emp.location_id))]), fill_value=0)
    assert (sizes < 5).any()


def test_planted_missing_language_preference(data_dir):
    emp = read(data_dir, "employees")
    share = emp.language_preference.isna().mean()
    assert 0 < share < 0.03


@pytest.mark.parametrize("a,b,expected", [
    ("2025-01-01", "2025-01-31", 23),
    ("2025-02-03", "2025-02-10", 6),
    ("2025-03-01", "2025-03-02", 0),
    ("2025-03-05", "2025-03-05", 1),
])
def test_weekday_counter(a, b, expected):
    import datetime as dt
    assert gd.weekdays_between(dt.date.fromisoformat(a), dt.date.fromisoformat(b)) == expected
