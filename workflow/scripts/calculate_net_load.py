if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    import sys
    sys.path.append("../utils")
    from utils import get_power_from_curve

    wind_df = pd.read_csv(snakemake.input.era5, 
                          parse_dates=True, 
                          index_col='valid_time', 
                          usecols=['valid_time','u100','v100'])
    load_df = pd.read_csv(snakemake.input.demand, 
                          parse_dates=True, 
                          index_col='BeginDate', 
                          usecols=['BeginDate','NativeLoad'])


    wind_df.index = wind_df.index.tz_localize('UTC').tz_convert('US/Eastern')
    wind_df = wind_df.reindex(load_df.index).dropna(axis=0)

    wind_df['U'] = np.sqrt(wind_df['u100']**2 + wind_df['v100']**2)
    wind_df['CF'] = wind_df.U.apply(get_power_from_curve)

    osw_capacity = snakemake.config['osw_capacity']
    eta = snakemake.config['efficiency']
    load_df[f'NetLoad{osw_capacity}MW'] = load_df.NativeLoad - (wind_df.CF*osw_capacity*eta)

    load_df.to_csv(snakemake.output.net_load)