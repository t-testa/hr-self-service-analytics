import pandas as pd
import pytest

import reference_kpis as rk

DEPTS = pd.DataFrame({"department_id": ["A", "B"], "department_name_en": ["Alpha", "Beta"]})
LOCS = pd.DataFrame({"location_id": ["X"], "city_en": ["Xville"]})
LEVELS = pd.DataFrame({"job_level_id": ["JL1"], "level_name_en": ["Junior"]})


def emp(eid, dept, hire="2020-01-01", term=None, ttype=None):
    return dict(employee_id=eid, hire_date=pd.Timestamp(hire),
                termination_date=pd.Timestamp(term) if term else pd.NaT,
                termination_type=ttype, department_id=dept, job_level_id="JL1",
                location_id="X", employment_type="Full-time")


@pytest.fixture(scope="module")
def small():
    """Hand-built case, Jan to Mar 2025.

    Dept Alpha: E1 to E6 hired 2020, E7 hired 2025-01-15.
      E1 leaves voluntarily 2025-02-10, E2 leaves involuntarily 2025-03-05.
      Month-end headcount: Jan 7, Feb 6, Mar 5. Average 6.
      Weekdays worked: E1 29, E2 46, E3 to E6 64 each, E7 54, total 385.
    Dept Beta: B1 and B2 only, so always below the minimum group size.
    """
    employees = pd.DataFrame(
        [emp("E1", "A", term="2025-02-10", ttype="voluntary"),
         emp("E2", "A", term="2025-03-05", ttype="involuntary")]
        + [emp("E%d" % i, "A") for i in range(3, 7)]
        + [emp("E7", "A", hire="2025-01-15")]
        + [emp("B1", "B"), emp("B2", "B")])
    absences = pd.DataFrame(
        [("E3", "2025-01-06", "Sick", 7.5), ("E3", "2025-02-03", "Personal", 3.75),
         ("E4", "2025-01-07", "Vacation", 7.5)], columns=["employee_id", "date", "type", "hours"])
    absences["date"] = pd.to_datetime(absences["date"])
    base = dict(department_id="A", location_id="X", job_level_id="JL1", employment_type="Full-time", reason="Backfill")
    rows = [dict(base, requisition_id="R%d" % i, open_date=pd.Timestamp("2025-01-01"), status="Filled",
                 filled_date=pd.Timestamp("2025-02-15"), days_to_fill=d) for i, d in enumerate([20, 30, 40, 50, 60])]
    rows += [dict(base, department_id="B", requisition_id="RB%d" % i, open_date=pd.Timestamp("2025-01-01"),
                  status="Filled", filled_date=pd.Timestamp("2025-03-10"), days_to_fill=d)
             for i, d in enumerate([10, 100])]
    rows.append(dict(base, requisition_id="ROPEN", open_date=pd.Timestamp("2025-03-01"), status="Open",
                     filled_date=pd.NaT, days_to_fill=None))
    long, wide = rk.compute(employees, absences, pd.DataFrame(rows), DEPTS, LOCS, LEVELS, "2025-01-01", "2025-03-31")
    return long, wide


def row(wide, ptype, period, dim, member):
    sel = wide[(wide.period_type == ptype) & (wide.period == period) & (wide.dimension == dim) & (wide.member == member)]
    assert len(sel) == 1
    return sel.iloc[0]


def test_headcount_hires_and_exits(small):
    r = row(small[1], "Quarter", "2025-Q1", "Department", "Alpha")
    assert r.headcount == 5
    assert r.hires == 1
    assert r.voluntary_terminations == 1 and r.involuntary_terminations == 1
    assert r.group_size == 5.0  # min(average 6, period end 5)


def test_turnover_is_annualized_on_average_headcount(small):
    q = row(small[1], "Quarter", "2025-Q1", "Department", "Alpha")
    assert q.voluntary_turnover_rate == pytest.approx(1 / 6 * 12 / 3)
    m = row(small[1], "Month", "2025-02", "Department", "Alpha")
    assert m.voluntary_turnover_rate == pytest.approx(1 / 6 * 12)  # single month: 12 / 1


def test_absence_rate_excludes_vacation(small):
    r = row(small[1], "Quarter", "2025-Q1", "Department", "Alpha")
    assert r.absence_rate == pytest.approx(11.25 / (385 * 7.5), abs=1e-6)


def test_time_to_fill_is_mean_of_filled_requisitions(small):
    assert row(small[1], "Quarter", "2025-Q1", "Department", "Alpha").avg_time_to_fill_days == 40.0
    assert row(small[1], "Quarter", "2025-Q1", "All", "All").avg_time_to_fill_days == pytest.approx(310 / 7, abs=0.01)


def test_company_level_totals(small):
    r = row(small[1], "Quarter", "2025-Q1", "All", "All")
    assert r.headcount == 7
    assert r.voluntary_turnover_rate == pytest.approx(1 / 8 * 12 / 3)  # average headcount 9, 8, 7


def test_minimum_group_size_suppresses_everything(small):
    r = row(small[1], "Quarter", "2025-Q1", "Department", "Beta")
    assert r.suppressed == "Yes"
    for col in ["headcount", "hires", "voluntary_turnover_rate", "involuntary_turnover_rate", "absence_rate"]:
        assert pd.isna(r[col])
    long = small[0]
    sel = long[(long.member == "Beta") & (long.period == "2025-Q1")]
    assert (sel[sel.kpi != "avg_time_to_fill_days"].status == "Not enough data").all()


def test_time_to_fill_needs_five_filled_requisitions(small):
    r = row(small[1], "Quarter", "2025-Q1", "Department", "Beta")
    assert r.ttf_suppressed == "Yes" and pd.isna(r.avg_time_to_fill_days)
    assert r.filled_requisitions == 2


def test_group_of_exactly_five_is_shown(small):
    r = row(small[1], "Quarter", "2025-Q1", "Department", "Alpha")
    assert r.suppressed == "No"  # size 5.0 is not below 5


def test_period_labels_and_latest_flags(small):
    wide = small[1]
    assert set(wide[wide.period_type == "Year"].period) == {"2025 YTD"}
    assert set(wide[wide.period_type == "Quarter"].period) == {"2025-Q1"}
    latest = wide[(wide.is_latest == "Yes")].groupby("period_type").period.first()
    assert latest["Month"] == "2025-03"


def test_real_data_agrees_with_fact_tables(data_dir):
    """The raw-table calculation must agree with the pre-built fact files."""
    inputs = rk.load_inputs(data_dir)
    long, wide = rk.compute(**inputs, start="2024-01-01", as_of="2026-09-30")
    snap = pd.read_csv(data_dir / "fact_headcount_snapshot.csv")
    for month in ["2024-01", "2025-06", "2026-09"]:
        expected = snap[snap.snapshot_date.str.startswith(month)].active_at_month_end.sum()
        assert row(wide, "Month", month, "All", "All").headcount == expected
    hires = snap[snap.snapshot_date.str.startswith("2025")].hired_in_month.sum()
    assert row(wide, "Year", "2025", "All", "All").hires == hires
    terms = pd.read_csv(data_dir / "fact_terminations.csv")
    vol = ((terms.termination_type == "voluntary") & terms.termination_date.str.startswith("2025")).sum()
    assert row(wide, "Year", "2025", "All", "All").voluntary_terminations == vol


def test_real_data_group_size_rule_and_outputs(data_dir):
    inputs = rk.load_inputs(data_dir)
    long, wide = rk.compute(**inputs, start="2024-01-01", as_of="2026-09-30")
    shown = wide[wide.suppressed == "No"]
    assert (shown[shown.dimension != "All"].group_size >= rk.MIN_GROUP_SIZE).all()
    hidden = wide[wide.suppressed == "Yes"]
    assert len(hidden) > 0
    assert hidden[["group_size", "headcount", "hires", "voluntary_turnover_rate", "absence_rate"]].isna().all().all()
    hidden_long = long[(long.suppressed == "Yes")]
    assert hidden_long.group_size.isna().all() and hidden_long.value.isna().all()
    assert (wide.groupby("period_type").is_latest.apply(lambda s: (s == "Yes").sum() > 0)).all()
    assert row(wide, "Year", "2026 YTD", "All", "All").months_in_period == 9


def test_agent_facts_never_contain_hidden_group_data(data_dir):
    inputs = rk.load_inputs(data_dir)
    long, wide = rk.compute(**inputs, start="2024-01-01", as_of="2026-09-30")
    text = rk.agent_facts_markdown(wide, inputs["departments"], inputs["locations"], inputs["job_levels"])
    line = [l for l in text.splitlines() if "Legal (Affaires juridiques) | Quebec City" in l and l.startswith("- 2026-Q3")][0]
    assert "NOT ENOUGH DATA" in line
    assert not any(ch.isdigit() for ch in line.split(":", 2)[2].replace("5", ""))  # no numbers except the minimum size 5
    assert "37.5%" in text  # Operations 2026-Q3 voluntary turnover is present elsewhere
