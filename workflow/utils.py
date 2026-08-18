from scipy.interpolate import interp1d
import numpy as np

# power curve values are based on NREL reference osw 12 mw turbine

turbine_power_curve = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: .048,
    5: .08,
    6: .15,
    7: .25,
    8: .39,
    9: .56,
    10: .77,
    11: 1,
    24: 1,
    25: 0,
}


def get_power_from_curve(wind_speed, power_curve_data=turbine_power_curve):
    """
    Estimates wind power capacity factor using a turbine's power curve.

    Args:
        wind_speed (float): Wind speed in meters per second (m/s).
        power_curve_data (dict): A dictionary where keys are wind speeds (m/s)
                                 and values are corresponding capacity factors.

    Returns:
        float: Estimated wind capacity factor.
    """
    wind_speeds = np.array(list(power_curve_data.keys()))
    power_outputs_cf = np.array(list(power_curve_data.values()))

    # Create an interpolation function
    f = interp1d(wind_speeds, power_outputs_cf, kind='linear', fill_value="extrapolate")

    return f(wind_speed)
