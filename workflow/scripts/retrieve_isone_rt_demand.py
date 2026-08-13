if __name__=="__main__":
    import pandas as pd
    import requests
    import json
    from tqdm import tqdm

    BASE_URL = "https://webservices.iso-ne.com/api/v1.1"
    market = "realtimehourlydemand"
    fmt = ".json"
    dates = pd.date_range(snakemake.config['start_date'],snakemake.config['end_date'], freq='D')
    location_ids = list(range(4001,4009))

    auth = (
            snakemake.params.username, 
            snakemake.params.password
            )
    full_frames = []
    for d in tqdm(dates):
        frames = []
        for loc in location_ids:
            url = "/".join([BASE_URL, 
                            market, 
                            'day', 
                            d.strftime("%Y%m%d"), 
                            'location', 
                            str(loc)]) + fmt
            r = requests.get(url, auth=auth, headers={"Accept":"application/json"})
            if r.status_code != 200:
                print(f"Status Code: {r.status_code} for url: {url}")
            data = r.json()['HourlyRtDemands']['HourlyRtDemand']
            df = pd.DataFrame(data)
            df['BeginDate'] = pd.to_datetime(df['BeginDate'], utc=False)
            df = df[['BeginDate', 'Load']]
            df.columns = ['datetime',loc]
            df.set_index('datetime', inplace=True)
            frames.append(df)
        full_frames.append(pd.concat(frames, axis=1))

    full_df = pd.concat(full_frames).sum()
    full_df.to_csv(snakemake.output.demand_data)