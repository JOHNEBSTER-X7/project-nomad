import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.energy_budget import calculate_daily_energy
from scripts.api_benchmark import percentile, run_benchmark


def test_energy_budget_calculates_daily_load_and_sizing():
    result = calculate_daily_energy([{"name": "server", "watts": 100, "hours_per_day": 10}])
    assert result["load_daily_wh"] == 1000
    assert result["estimated_dc_daily_wh"] > 1000
    assert result["estimated_battery_nominal_wh"] > result["estimated_dc_daily_wh"]
    assert result["estimated_solar_array_w"] > 0


def test_energy_budget_rejects_invalid_efficiency():
    with pytest.raises(ValueError):
        calculate_daily_energy([], inverter_efficiency=0)


def test_percentile_handles_empty_and_values():
    assert percentile([], .95) is None
    assert percentile([1, 2, 3, 4, 5], .95) == 5


def test_api_benchmark_rejects_invalid_workload():
    with pytest.raises(ValueError):
        run_benchmark("http://127.0.0.1:1", requests=0)
