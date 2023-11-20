# TODO (2023-11-15)
# * fill in missing "sleep" events
# * get the plot to show dates in order
# TODO (2023-11-19)
# * add birth event
# * handle overlapping events in aesthetically pleasing way
# * define color pallets (ask J & A)
# * make alternative formats for y-axis ticks (e.g. "Nov 2" instead of YYYY-MM-DD)
# * consider removing the min_hour/max_hour stuff

# imports
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import time
import util

# constants
BIRTHDAY = dt.date(2022, 11, 2)
BIRTHDAY_DT = dt.datetime(BIRTHDAY.year, BIRTHDAY.month, BIRTHDAY.day)
SECONDS_PER_HOUR = 60 * 60
HOURS_PER_DAY = 24
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

# %%
DF_ORIG = util.load_data()
df = DF_ORIG.copy(deep=True)
MINIMUM_DURATION = 5.0 * 60.0  # five minutes
df, event_column_dict = util.process_raw_data(df, time_unit='seconds', minimum_duration=MINIMUM_DURATION)

# %% plot prep
NUM_WEEKS_TO_PLOT = 52
plot_date_filters = [BIRTHDAY_DT, BIRTHDAY_DT + dt.timedelta(days=7 * NUM_WEEKS_TO_PLOT)]

# minimum and maximum hours of the day covered by the data. used to bound the plot
min_hour = HOURS_PER_DAY
max_hour = 0

# number of days to be included in a row
PLOT_ROW_SIZE = 7
# PLOT_ROW_SIZE = 1
df['days_from_bday'] = (df['date'] - BIRTHDAY).apply(lambda d: int(d.days))
df['col_num'] = (df['days_from_bday'] / PLOT_ROW_SIZE).astype(int)
df['row_num'] = df['days_from_bday'] - df['col_num'] * 7

BAR_HEIGHT = 0.8

# %%  T H E   P L O T
fig, ax = plt.subplots(
    # figsize=(30, 50)
    figsize=(20, BAR_HEIGHT * 2 * NUM_WEEKS_TO_PLOT)
)
for ET in df['type'].unique():#['Sleep', 'Feed']:
    # define the "event data frame", used for plotting events of a certain color
    edf = df[
        (df['start'] >= plot_date_filters[0]) &
        (df['start'] < plot_date_filters[1]) &
        (df['type'] == ET)
    ].sort_values('start', ascending=False)
    edf = edf.rename(columns=event_column_dict[ET])  # TODO: maybe remove this?
    if edf.shape[0] == 0:  # don't attempt to plot if there were no events of this type on this day
        continue

    for x in ['start', 'end']:
        # calculate start/end time as seconds from midnight
        edf[f'{x}_time'] = (
            edf[x] - edf['start'].apply(lambda d: dt.datetime(d.year, d.month, d.day))
        ).apply(lambda d: d.seconds)

        # modify the start and end times to place multiple days on a row, by adding the number of
        #  seconds in a day multiplied by the number of day it is in the row.
        # For instance, if we wanted to fit 7 days on a row, then we would add a number of seconds
        #  to the times for each event on that day that is equal to:
        #   7 * the number of seconds in a day
        edf[f'{x}_time'] += (edf['row_num'] * HOURS_PER_DAY * SECONDS_PER_HOUR)

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
    # plot bars
    plt.barh(
        y=(
            edf['start'].apply(util.my_date_conversion) -
            edf['row_num'].apply(lambda d: dt.timedelta(days=d))
        ).apply(lambda d: d.strftime('%Y-%m-%d')),
        # y=edf['start'].apply(lambda d: d.date().strftime('%Y-%m-%d')),
        width=edf['duration'],
        height=BAR_HEIGHT,
        left=edf['start_time'],
        label=ET,
        color=EVENT_COLOR_DICT[ET.lower()],
        alpha=0.5
    )

tick_type = 'day_of_week'
if tick_type == 'hour':
    if max_hour <= min_hour:  # last minute catch-all
        print(f'||| WARNING |||\nmax hour {max_hour} should be > min hour {min_hour}')
        min_hour, max_hour = 0, HOURS_PER_DAY
    # hour_step_size = 1
    # hour_step_size = 3
    hour_step_size = 6
    # hour_step_size = 12
    # hour_ticks = list(range(min_hour * 60 * 60, (max_hour + 1) * 60 * 60, 60 * 60))
    # hour_ticks = [*list(range(min_hour * 60 * 60, (max_hour + 1) * 60 * 60, 60 * 60))] * PLOT_ROW_SIZE
    hour_ticks = list(range(
        min_hour * SECONDS_PER_HOUR,
        ((max_hour * PLOT_ROW_SIZE) + 1) * SECONDS_PER_HOUR,
        hour_step_size * SECONDS_PER_HOUR
    ))
    hour_tick_labels = [util.convert_num_seconds_to_time_of_day(x) for x in hour_ticks]# * PLOT_ROW_SIZE
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_tick_labels)
elif tick_type == 'day_of_week':
    # this mode should only be used when PLOT_ROW_SIZE == 7
    dow_ticks = list(range(0, HOURS_PER_DAY * PLOT_ROW_SIZE * SECONDS_PER_HOUR, HOURS_PER_DAY * SECONDS_PER_HOUR))
    # dow_tick_labels = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue']
    dow_tick_labels = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    ax.set_xticks(dow_ticks)
    ax.set_xticklabels(dow_tick_labels)
    # OPTIONAL -- vertical lines at the start of each day
    for day_start_time in dow_ticks:
        plt.axvline(x=day_start_time, color='k', linestyle=':')
# plt.rcParams.update({'font.size': 12})
plt.legend()
plt.show()
# %%
