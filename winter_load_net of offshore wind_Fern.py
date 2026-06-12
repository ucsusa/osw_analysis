import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

#gather load data

# winter_daily_load = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\FERN 2026\ISO-NE Fern load profile(Sheet1).csv')
winter_daily_load = pd.read_csv('ISO-NE Fern load profile(Sheet1).csv')
winter_daily_load['Date'] = pd.to_datetime(winter_daily_load['Date'])
print(winter_daily_load)

#plot winter load

fig, ax = plt.subplots()
ax.plot(winter_daily_load['Date'],winter_daily_load['MWh'])
ax.set_title('Blackout Risk 2026 Extreme Cold Event')
ax.set_ylabel('Load (MWh)')
plt.title("Daily Energy Demand")
plt.ylabel("MWh")
plt.fill_between(winter_daily_load['Date'],350000,400000,color='yellow',alpha = 0.75,label = 'elevated risk')
plt.fill_between(winter_daily_load['Date'],400000,450000,color='orange',alpha = 0.75,label = 'high risk')
plt.show()

#gather offshore wind data 

from scipy.interpolate import interp1d
def get_power_from_curve(wind_speed, power_curve_data):
    """
    Estimates wind power output using a turbine's power curve.

    Args:
        wind_speed (float): Wind speed in meters per second (m/s).
        power_curve_data (dict): A dictionary where keys are wind speeds (m/s)
                                 and values are corresponding power outputs (Watts).

    Returns:
        float: Estimated wind power output in Watts.
    """
    wind_speeds = np.array(list(power_curve_data.keys()))
    power_outputs_cf = np.array(list(power_curve_data.values()))

    # Create an interpolation function
    f = interp1d(wind_speeds, power_outputs_cf, kind='linear', fill_value="extrapolate")

    return f(wind_speed)

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
    25: 1
}

#add January offshore wind speed

# grib_file_path1 = r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\FERN 2026\January offshore wind\January_osw.grib'
grib_file_path1 = 'January_osw.grib'
jan_wind = xr.load_dataset(grib_file_path1, engine='cfgrib')
jan_wind=jan_wind.sel(latitude=40.4, method='nearest', drop=True)
jan_wind=jan_wind.sel(longitude=-71.0, drop=True)
print(jan_wind)
u = jan_wind['u100']
v = jan_wind['v100']
jan_wind['wind_speed'] = np.sqrt(u**2 + v**2)
jan_wind['wind_speed'].plot()
plt.title("Hourly Wind Speed in Southern New England OSW Lease Area")
plt.xlabel("January 23-31 2026")
plt.ylabel("m/s")
#plt.show()

#calculate January offshore wind power

ws = jan_wind['wind_speed']
power_output_curve_cf = get_power_from_curve(ws, turbine_power_curve)
power_output = power_output_curve_cf

# reduce by 30% to account for wake effects, electrical losses and turbine unavailability

power_output = power_output*.7

#plot January offshore wind power

jan_power_df = pd.DataFrame(power_output, columns=['power'])
print(jan_power_df.head)
start_date = '2026-01-23 00:00:00'
jan_power_df['DateTime'] = pd.to_datetime(start_date) + pd.to_timedelta(jan_power_df.index, unit='h')
jan_power_df['power'].plot()
plt.title("Hourly OSW Power")
plt.xlabel("January 23-31 2026")
#plt.show()
jan_daily_power = jan_power_df.groupby(jan_power_df['DateTime'].dt.date)['power'].sum().reset_index()
print("This is January Power:", jan_daily_power)

#add February offshore wind speed

# grib_file_path2 = r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\FERN 2026\February offshore wind\February_osw.grib'
grib_file_path2 = 'February_osw.grib'
feb_wind = xr.load_dataset(grib_file_path2, engine='cfgrib')
feb_wind=feb_wind.sel(latitude=40.4, method='nearest', drop=True)
feb_wind=feb_wind.sel(longitude=-71.0, drop=True)
print(feb_wind)
u = feb_wind['u100']
v = feb_wind['v100']
feb_wind['wind_speed'] = np.sqrt(u**2 + v**2)
feb_wind['wind_speed'].plot()
plt.title("Hourly Wind Speed in Southern New England OSW Lease Area")
plt.xlabel("February 1-10 2026")
plt.ylabel("m/s")
#plt.show()

#calculate February offshore wind power

ws = feb_wind['wind_speed']
power_output_curve_cf = get_power_from_curve(ws, turbine_power_curve)
power_output = power_output_curve_cf

# reduce by 30% to account for wake effects, electrical losses and turbine unavailability

power_output = power_output*.7

#plot February offshore wind power

feb_power_df = pd.DataFrame(power_output, columns=['power'])
print(feb_power_df.head)
start_date = '2026-02-01 00:00:00'
feb_power_df['DateTime'] = pd.to_datetime(start_date) + pd.to_timedelta(feb_power_df.index, unit='h')
feb_power_df['power'].plot()
plt.title("Hourly OSW Power")
plt.xlabel("February 1-10 2026")
#plt.show()
feb_daily_power = feb_power_df.groupby(feb_power_df['DateTime'].dt.date)['power'].sum().reset_index()
print(feb_daily_power)

#combine January and February offshore wind power

winter_daily_power = pd.concat([jan_daily_power, feb_daily_power])
winter_daily_power = winter_daily_power.rename(columns={'DateTime':'Date'})

# calculate the total daily energy from offshore wind fleets of 1500MW and 3500MW

winter_daily_power['1500MW'] = winter_daily_power['power']*1500
winter_daily_power['3500MW'] = winter_daily_power['power']*3500
print(winter_daily_power)
total_1500mw_osw_energy = (winter_daily_power['1500MW']).sum()
total_3500mw_osw_energy = (winter_daily_power['3500MW']).sum()
print("total energy delivered by a 1500MW offshore wind fleet:", total_1500mw_osw_energy)
print("total energy delivered by a 3500MW offshore wind fleet:", total_3500mw_osw_energy)
#print(winter_daily_power.dtypes)
#print(winter_daily_load.dtypes)
winter_daily_power['Date']=pd.to_datetime(winter_daily_power['Date'])
#winter_daily_power.to_csv('winter_daily-power.csv')
#print(winter_daily_power.dtypes)

#subtract offshore wind from load to determine net load

winter_load_net_of_offshore_wind = pd.merge(winter_daily_load,winter_daily_power,on = "Date", how = "left")
winter_load_net_of_offshore_wind['load_net_1500MW_osw']=winter_load_net_of_offshore_wind['MWh']-winter_load_net_of_offshore_wind['1500MW']
winter_load_net_of_offshore_wind['load_net_3500MW_osw']=winter_load_net_of_offshore_wind['MWh']-winter_load_net_of_offshore_wind['3500MW']
winter_load_net_of_offshore_wind.to_csv('winter_load_net_of_offshore_wind.csv')
print(winter_load_net_of_offshore_wind)


#plot the daily load net of offshore wind energy

fig, ax = plt.subplots()
ax.plot(winter_load_net_of_offshore_wind['Date'],winter_load_net_of_offshore_wind['MWh'],label='Daily Energy Demand', color='black')
ax.plot(winter_load_net_of_offshore_wind['Date'],winter_load_net_of_offshore_wind['load_net_1500MW_osw'],label='Demand net of 1500MW offshore wind', color = 'lightblue')
ax.plot(winter_load_net_of_offshore_wind['Date'],winter_load_net_of_offshore_wind['load_net_3500MW_osw'],label='Demand net of 3500MW offshore wind', color = 'blue')
plt.title("New England Blackout Risk 2026 Extreme Cold Event")
plt.ylabel("Daily Energy Demand (MWh)")
plt.fill_between(winter_daily_load['Date'],350000,400000,color='yellow',alpha = 0.75,label = 'Elevated risk of blackout')
plt.fill_between(winter_daily_load['Date'],400000,450000,color='orange',alpha = 0.75,label = 'Higher risk of blackout')
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
plt.show()

# tally days with elevated and higher risk before and after accounting for offshore wind

winter_daily_load['elevated risk status']=winter_daily_load['MWh']-350000
winter_daily_load['higher risk status']=winter_daily_load['MWh']-400000
elevated_risk_days = (winter_daily_load['elevated risk status'] > 0).sum()
higher_risk_days = (winter_daily_load['higher risk status'] > 0).sum()
print("days with elevated risk:", elevated_risk_days)
print("days with higher risk:", higher_risk_days)
winter_load_net_of_offshore_wind ['elevated risk after 1500mw osw']=winter_load_net_of_offshore_wind['load_net_1500MW_osw']-350000
winter_load_net_of_offshore_wind ['elevated risk after 3500mw osw']=winter_load_net_of_offshore_wind['load_net_3500MW_osw']-350000
winter_load_net_of_offshore_wind ['higher risk after 1500mw osw']=winter_load_net_of_offshore_wind['load_net_1500MW_osw']-400000
winter_load_net_of_offshore_wind ['higher risk after 3500mw osw']=winter_load_net_of_offshore_wind['load_net_3500MW_osw']-400000
elevated_risk_days_1500mw = (winter_load_net_of_offshore_wind['elevated risk after 1500mw osw'] > 0).sum ()
elevated_risk_days_3500mw = (winter_load_net_of_offshore_wind['elevated risk after 3500mw osw'] > 0).sum ()
higher_risk_days_1500mw = (winter_load_net_of_offshore_wind['higher risk after 1500mw osw'] > 0).sum ()
higher_risk_days_3500mw = (winter_load_net_of_offshore_wind['higher risk after 3500mw osw'] > 0).sum ()
print("days with elevated risk after 1500mw osw:", elevated_risk_days_1500mw)
print("days with elevated risk after 3500mw osw:", elevated_risk_days_3500mw)
print("days with higher risk after 1500mw osw:", higher_risk_days_1500mw)
print("days with higher risk after 3500mw osw:", higher_risk_days_3500mw)

#plot days with risk
#plot the daily load net of offshore wind energy

fig, ax = plt.subplots()
ax.plot(winter_load_net_of_offshore_wind['Date'],winter_load_net_of_offshore_wind['MWh'],label='Daily Energy Demand', color='black')
ax.plot(winter_load_net_of_offshore_wind['Date'],winter_load_net_of_offshore_wind['load_net_1500MW_osw'],label='Demand net of 1500MW offshore wind', color = 'lightblue')
ax.plot(winter_load_net_of_offshore_wind['Date'],winter_load_net_of_offshore_wind['load_net_3500MW_osw'],label='Demand net of 3500MW offshore wind', color = 'blue')
plt.title("New England Blackout Risk 2026 Extreme Cold Event")
plt.ylabel("Daily Energy Demand (MWh)")
plt.fill_between(winter_daily_load['Date'],350000,400000,color='yellow',alpha = 0.75,label = 'Elevated risk of blackout')
plt.fill_between(winter_daily_load['Date'],400000,450000,color='orange',alpha = 0.75,label = 'Higher risk of blackout')
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
rows = ('Days with elevated risk', 'Days with higher risk')
columns = ('Daily Energy Demand', 'Demand Net of 1500 MW OSW', 'Demand Net of 3500 MW OSW')
risk_table = ax.table( cellText= [(elevated_risk_days,elevated_risk_days_1500mw,elevated_risk_days_3500mw),(higher_risk_days,higher_risk_days_1500mw,higher_risk_days_3500mw)], rowLabels=rows, colLabels=columns, loc='bottom')
plt.text(.2,0,'days with risk')
plt.show()