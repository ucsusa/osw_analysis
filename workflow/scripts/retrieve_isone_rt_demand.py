if __name__=="__main__":
    import pandas as pd
    import requests
    import json
    from tqdm import tqdm

    BASE_URL = "https://webservices.iso-ne.com/api/v1.1"
    market = 'hourlysysload'
    fmt = ".json"
    dates = pd.date_range(snakemake.config['start_date'],snakemake.config['end_date'], freq='D')
    # location_ids = list(range(4001,4009))

    auth = (
            snakemake.params.username, 
            snakemake.params.password
            )
    frames = []
    for d in tqdm(dates):
        url = "/".join([BASE_URL, 
                        market, 
                        'day', 
                        d.strftime("%Y%m%d"), 
                        ]
                        ) + fmt
        r = requests.get(url, auth=auth, headers={"Accept":"application/json"})
        if r.status_code != 200:
            print(f"Status Code: {r.status_code} for url: {url}")
        df = pd.DataFrame(r.json()['HourlySystemLoads']['HourlySystemLoad'])
        df['BeginDate'] = pd.to_datetime(df['BeginDate'], utc=False)
        df = df[['BeginDate', 'Load','NativeLoad','ArdDemand']]
        df.set_index('BeginDate', inplace=True)
        frames.append(df)

    full_df = pd.concat(full_frames)
    full_df.to_csv(snakemake.output.demand_data)