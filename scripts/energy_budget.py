#!/usr/bin/env python3
"""Transparent first-pass daily energy budget calculator; estimates are not site measurements."""
import argparse
import json


def calculate_daily_energy(loads: list[dict], system_voltage: float = 24.0,
                           usable_battery_fraction: float = 0.8,
                           inverter_efficiency: float = 0.9,
                           peak_sun_hours: float = 4.0,
                           solar_derate: float = 0.75) -> dict:
    if system_voltage <= 0 or peak_sun_hours <= 0:
        raise ValueError("system_voltage and peak_sun_hours must be positive")
    if not 0 < usable_battery_fraction <= 1 or not 0 < inverter_efficiency <= 1 or not 0 < solar_derate <= 1:
        raise ValueError("fractions and efficiencies must be greater than 0 and at most 1")
    total_wh = 0.0
    breakdown = []
    for item in loads:
        watts = float(item["watts"])
        hours = float(item["hours_per_day"])
        quantity = int(item.get("quantity", 1))
        if watts < 0 or hours < 0 or quantity < 1:
            raise ValueError("load watts/hours must be non-negative and quantity at least 1")
        wh = watts * hours * quantity
        total_wh += wh
        breakdown.append({"name": str(item.get("name", "unnamed")), "daily_wh": round(wh, 1)})
    dc_daily_wh = total_wh / inverter_efficiency
    battery_nominal_wh = dc_daily_wh / usable_battery_fraction
    solar_array_w = dc_daily_wh / (peak_sun_hours * solar_derate)
    return {
        "schema_version": 1,
        "load_daily_wh": round(total_wh, 1),
        "estimated_dc_daily_wh": round(dc_daily_wh, 1),
        "estimated_battery_nominal_wh": round(battery_nominal_wh, 1),
        "estimated_battery_ah": round(battery_nominal_wh / system_voltage, 1),
        "estimated_solar_array_w": round(solar_array_w, 1),
        "assumptions": {"system_voltage": system_voltage, "usable_battery_fraction": usable_battery_fraction,
                        "inverter_efficiency": inverter_efficiency, "peak_sun_hours": peak_sun_hours,
                        "solar_derate": solar_derate},
        "loads": breakdown,
        "notice": "Preliminary sizing estimate only. Validate measured loads, local solar resource, autonomy days, battery chemistry, temperature, surge, wiring, protection and applicable electrical codes with a qualified installer."
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loads-json", required=True, help='JSON array, e.g. \'[{"name":"server","watts":120,"hours_per_day":24}]\'')
    parser.add_argument("--voltage", type=float, default=24.0)
    parser.add_argument("--sun-hours", type=float, default=4.0)
    args = parser.parse_args()
    loads = json.loads(args.loads_json)
    if not isinstance(loads, list):
        parser.error("--loads-json must decode to a JSON array")
    print(json.dumps(calculate_daily_energy(loads, system_voltage=args.voltage,
                                            peak_sun_hours=args.sun_hours), indent=2))


if __name__ == "__main__":
    main()
