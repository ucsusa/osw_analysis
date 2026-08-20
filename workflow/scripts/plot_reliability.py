if __name__ == "__main__":

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    try:
        import UCSmpl
        style = 'ucs_light'
    except:
        style = 'default'

    print(style)


    net_load_df = pd.read_csv(snakemake.input.net_load, 
                              parse_dates=True, 
                              index_col='BeginDate'
                              )

    net_load_df = net_load_df.resample('D').sum().loc[:'2026-02-10']

    ebr_thresh = snakemake.config['Elevated Blackout Risk']
    hbr_thresh = snakemake.config["Higher Blackout Risk"]

    with plt.style.context(style):
        fig, ax = plt.subplots(figsize=(10,6))

        net_load_df.plot(ax=ax, zorder=10)

        ax.fill_between(x = net_load_df.index, y1=ebr_thresh, y2=hbr_thresh, color='gold', alpha=0.5, label='Elevated Blackout Risk')
        ax.fill_between(x = net_load_df.index, y1=hbr_thresh, y2=hbr_thresh+100e3, color='crimson', alpha=0.5, label='Higher Blackout Risk')

        ax.set_ylim(300e3, hbr_thresh+50e3)
        ax.legend()

        plt.savefig(snakemake.output[0])

