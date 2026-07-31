import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pytz


#gather winter load data

dec_load1 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\DECEMBER\rt_hourlysysload_20241201_20241215.csv')
dec_load2 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\DECEMBER\rt_hourlysysload_20241216_20241230.csv')
dec_load3 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\DECEMBER\rt_hourlysysload_20241231.csv')
dec_load = pd.concat([dec_load1,dec_load2,dec_load3])

jan_load1 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\JANUARY\rt_hourlysysload_20250101_20250115.csv')
jan_load2 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\JANUARY\rt_hourlysysload_20250116_20250130.csv')
jan_load3 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\JANUARY\rt_hourlysysload_20250131.csv')
jan_load = pd.concat([jan_load1,jan_load2,jan_load3])

feb_load1 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\FEBRUARY\rt_hourlysysload_20250201_20250214.csv')
feb_load2 = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\LOAD\FEBRUARY\rt_hourlysysload_20250215_20250228.csv')
feb_load = pd.concat([feb_load1,feb_load2])

winter_load = pd.concat([dec_load,jan_load,feb_load])
winter_load = winter_load.drop(columns=['H'])
winter_load['Date'] = pd.to_datetime(winter_load['Date'])
winter_daily_load = winter_load.groupby('Date')['MWh'].sum().reset_index()
print(winter_daily_load)


#plot winter load

fig, ax = plt.subplots()
#ax.plot(winter_daily_load['Date'],winter_daily_load['MWh'])
#ax.set_title('Blackout Risk Winter 2024-25')
#ax.set_ylabel('Load (MWh)')
#plt.title("Daily Energy Demand")
#plt.ylabel("MWh")
#plt.fill_between(winter_load['Date'],350000,400000,color='yellow',alpha = 0.75,label = 'elevated risk')
#plt.fill_between(winter_load['Date'],400000,450000,color='orange',alpha = 0.75,label = 'high risk')
#plt.show()


#gather hourly offshore wind speed data 

winter_wind = pd.read_csv(r'C:\Users\smuller\OneDrive - Union of Concerned Scientists\Desktop\PYTHON PROJECT\DATA\WIND\offshore wind speed.csv')
u = winter_wind['u100']
v = winter_wind['v100']
winter_wind['wind_speed'] = np.sqrt(u**2 + v**2)
winter_wind['DateTime_UTC'] = pd.to_datetime(winter_wind['DateTime_UTC'])
print()
print("This is winter hourly wind speed in UTC:")
print()
print(winter_wind)
winter_wind['wind_speed'].plot()
plt.title("Hourly Wind Speed in Southern New England OSW Lease Area")
plt.xlabel("Winter 2024-2025")
plt.ylabel("m/s")
plt.show()


#convert to EST

#local_timezone = pytz.timezone('US/Eastern')
#winter_wind['DateTime_EST'] = winter_wind['DateTime_UTC'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
#print()
#print('This is winter hourly wind speed in UTC and EST:')
#print()
#print(winter_wind)
#winter_wind.to_csv("winter hourly wind speed in UTC and EST.csv")
#winter_wind['Date'] = winter_wind['DateTime_EST']

#calculate hourly offshore wind power

ws = winter_wind['wind_speed']
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
power_output_curve_cf = get_power_from_curve(ws, turbine_power_curve)
power_output = power_output_curve_cf

# reduce by 30% to account for wake effects, electrical losses and turbine unavailability

power_output = power_output*.7

winter_power = pd.DataFrame(power_output, columns=['power'])
print("This is winter hourly power:")
print(winter_power.head)

# convert to DateTime format (UTC by default)

start_date = '2024-12-01 00:00:00'
winter_power['DateTime_UTC'] = pd.to_datetime(start_date) + pd.to_timedelta(winter_power.index, unit='h')
print()
print("This is winter hourly power in UTC:")
print()
print(winter_power.head)
winter_power.to_csv('Winter hourly power in UTC.csv')

# convert to EST

local_timezone = pytz.timezone('US/Eastern')
winter_power['DateTime_EST'] = winter_power['DateTime_UTC'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
print()
print('This is winter hourly power in UTC and EST:')
print()
print(winter_power)
winter_power.to_csv("Winter hourly power in UTC and EST.csv")

#winter_power['Date'] = winter_power['DateTime_EST']


winter_power['power'].plot()
plt.title("Hourly OSW power")
plt.xlabel("Winter 2024-2025")
plt.show()

#calculate daily offshore wind power

winter_daily_power = winter_power.groupby(winter_power['DateTime_EST'].dt.date)['power'].sum().reset_index()
winter_daily_power = winter_daily_power.rename(columns={'DateTime_EST':'Date'})
winter_daily_power['Date'] = pd.to_datetime(winter_daily_power['Date'])
print()
print("This is winter daily power in EST:")
print()
print(winter_daily_power)

#drop dates outside of study time period

winter_daily_power = winter_daily_power[winter_daily_power['Date'].between('2024-12-01','2025-02-28')]
print()
print("This is winter daily power in the study period:")
print()
print(winter_daily_power)

# calculate the total daily energy from offshore wind fleets of 1500MW and 3500MW

winter_daily_power['1500MW'] = winter_daily_power['power']*1500
winter_daily_power['3500MW'] = winter_daily_power['power']*3500
print()
print("This is winter daily power from a 1500MW and 3500MW fleet:")
print()
print(winter_daily_power)

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
#plt.title("Blackout Risk Winter 2024-25")
plt.ylabel("Daily Energy Demand (MWh)")
plt.fill_between(winter_load['Date'],350000,400000,color='yellow',alpha = 0.75,label = 'Elevated risk of blackout')
plt.fill_between(winter_load['Date'],400000,450000,color='orange',alpha = 0.75,label = 'Higher risk of blackout')
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
#plt.title("Blackout Risk Winter 2024-25")
plt.ylabel("Daily Energy Demand (MWh)")
plt.fill_between(winter_load['Date'],350000,400000,color='yellow',alpha = 0.75,label = 'Elevated risk of blackout')
plt.fill_between(winter_load['Date'],400000,450000,color='orange',alpha = 0.75,label = 'Higher risk of blackout')
plt.legend(bbox_to_anchor=(1,1), loc="upper left")
rows = ('Days with elevated risk', 'Days with higher risk')
columns = ('Daily Energy Demand', 'Demand Net of 1500 MW OSW', 'Demand Net of 3500 MW OSW')
risk_table = ax.table( cellText= [(elevated_risk_days,elevated_risk_days_1500mw,elevated_risk_days_3500mw),(higher_risk_days,higher_risk_days_1500mw,higher_risk_days_3500mw)], rowLabels=rows, colLabels=columns, loc='bottom')
plt.text(.2,0,'days with risk')
plt.show()

# season view

total_winter_power = (winter_daily_power['power']).sum()
total_winter_power_1500 = total_winter_power*1500
total_winter_power_3500 = total_winter_power*3500
print("Total winter power:", total_winter_power)
print()
print("Total power from a 1500 MW fleet:", total_winter_power_1500)
print()
print("Total power from a 3500 MW fleet:", total_winter_power_3500)