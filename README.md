The analysis in this repository assesses the potential contribution of offshore wind to reducing the risk of power outages in New England, particularly in winter, based on a key reliability metric. It builds on work led by Susan Muller of the Union of Concerned Scientists, including New England’s Offshore Wind Solution (February 2026; https://www.ucs.org/resources/new-englands-offshore-wind-solution).

The analysis involves
* Calculating daily electricity demand in the region by pulling and summing hourly data from ISO-NE, the regional electric grid operator
* Calculating daily offshore wind energy potential by pulling indicative hourly wind speed data from the Copernicus Climate Change Service’s ERA5, converting those data to hourly capacity factors using turbine information from the National Laboratory of the Rockies, calculating theoretical generation from defined levels of offshore wind (OSW) turbine capacity, and summing that generation
* Calculating daily electricity demand net of OSW electricity

The results show the extent to which OSW could have reduced the risk of an energy shortfall during periods of elevated demand-driven blackout risk (which ISO-NE defines as daily energy demand above 350,000 megawatt-hours) and higher blackout risk (when demand was above 400,000 MWh).
