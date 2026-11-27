# Energy measurement protocol

1. Use a suitably rated, calibrated energy meter installed by a qualified person. Do not open electrical equipment or modify mains wiring as part of software testing.
2. Record the meter model, measurement boundary, accuracy class, units and calibration date.
3. Measure the system in defined states: powered off, idle, typical portal/search activity, local AI inference, indexing, and peak combined workload.
4. Record average watts, peak watts, accumulated watt-hours, duration, ambient temperature and any thermal throttling.
5. For solar/battery tests, separately record PV input, battery voltage/current/state of charge, charge-controller readings, inverter losses and load energy where safely measurable.
6. Capture at least a full representative daily cycle and note weather, shading and seasonal limitations. One sunny-day test is not an annual energy assessment.
7. Estimate autonomy using measured daily energy and the battery manufacturer's permitted depth of discharge, temperature derating and conversion losses.
8. Have a qualified local electrical/solar professional review cable sizing, fusing, earthing, surge/lightning protection, ventilation, fire safety and applicable standards.

Never treat the repository calculator as an installation design. It is a transparent first-pass arithmetic aid; final sizing requires site-specific engineering.
