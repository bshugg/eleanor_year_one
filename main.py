# TODO (2023-11-15)
# * fill in missing "sleep" events
# * get the plot to show dates in order
# * re-organize the plot to show, for instance, 52 columns of 7 days worth of data; or one month; or something else etc.

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import time
import util

EVENT_COLOR_DICT = {
    'sleep': 'black',
    'feed': 'limegreen',
    'solids': 'forestgreen',
    'diaper': 'saddlebrown',
    'meds': 'red',
    'bath': 'blue',
    'brush teeth': 'pink',
    'tummy time': 'yellow',
    'skin to skin': 'orange',
    'indoor play': 'purple',
    'outdoor play': 'magenta'
}

if __name__ == "__main__":
    df = util.load_data()
    MINIMUM_DURATION = 5.0 * 60.0  # five minutes
    df, event_column_dict = util.process_raw_data(df, time_unit='seconds', minimum_duration=MINIMUM_DURATION)

    plot_date_filters = [
        # dt.datetime(2023, 11, 2), dt.datetime(2023, 11, 5)
        # dt.datetime(2022, 11, 2), dt.datetime(2022, 12, 3)
        dt.datetime(2023, 1, 1),
        dt.datetime(2023, 6, 1)
    ]

    # minimum and maximum hours of the day covered by the data. used to bound the plot
    min_hour = 24
    max_hour = 0

    fig, ax = plt.subplots(figsize=(30, 50))
    for ET in df['type'].unique():#['Sleep', 'Feed']:
        # "event data frame"
        edf = df[(df['start'] >= plot_date_filters[0]) & (df['start'] < plot_date_filters[1])].sort_values('start', ascending=False)
        edf = edf[edf['type'] == ET].rename(columns=event_column_dict[ET])
        edf['start_date'] = edf['start'].apply(lambda d: d.date())
        edf['end_date'] = edf['end'].apply(lambda d: d.date())

        # calculate start/end time as seconds from midnight
        edf['start_time'] = (edf['start'] - edf['start'].apply(lambda d: dt.datetime(d.year, d.month, d.day))).apply(lambda d: d.seconds)
        edf['end_time'] = (edf['end'] - edf['start'].apply(lambda d: dt.datetime(d.year, d.month, d.day))).apply(lambda d: d.seconds)

        try:
            # TODO: change this to a conditional that pre-selects out the NaT values
            # TODO: find out why there are NaT values
            min_hour = min(
                min_hour,
                time.gmtime(edf['start_time'].astype(int).min())[3],
                time.gmtime(edf['end_time'].astype(int).min())[3]
            )
            max_hour = max(
                max_hour,
                time.gmtime(edf['start_time'].astype(int).max())[3],
                time.gmtime(edf['end_time'].astype(int).max())[3]
            )
        except:
            pass
        plt.barh(
            y=edf['start'].apply(lambda d: d.date().strftime('%Y-%m-%d')),
            width=edf['duration'],
            # height=
            left=edf['start_time'],
            label=ET,
            color=EVENT_COLOR_DICT[ET.lower()],
            alpha=0.5
        )

    if max_hour <= min_hour:  # last minute catch-all
        min_hour, max_hour = 0, 24
    hour_ticks = list(range(min_hour * 60 * 60, (max_hour + 1) * 60 * 60, 60 * 60))
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels([util.convert_num_seconds_to_time_of_day(x) for x in hour_ticks])
    plt.legend()
    plt.show()
