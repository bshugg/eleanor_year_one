# TODO (2023-11-15)
# * fill in missing "sleep" events
# * get the plot to show dates in order
# TODO (2023-11-19)
# * handle overlapping events (in aesthetically pleasing way or by removing them)
# * define color pallets (ask J & A)
# * make alternative formats for y-axis ticks (e.g. "Nov 2" instead of YYYY-MM-DD)
# TODO (2023-11-20)
# * save plots in NEW output folder
# * share a version of plot with and without extrapolations with J&A

# %% imports
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import util
import constants
import extrapolator

EVENT_COLOR_DICT = {
    'birth': 'gold',
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

# %% load and process raw data
DF_ORIG = util.load_data()
df = DF_ORIG.copy(deep=True)
# %% rename all columns to lowercase
df = df.rename(columns={c: 'legacy_duration' if c == 'Duration' else c.lower() for c in df.columns})
# %% rename all event types to lowercase
df['type'] = df['type'].apply(lambda x: x.lower())
# %% remove event types that won't be covered
df = df[
    ~df['type'].isin([
        # column(s) with very few entries
        # 'brush teeth', 'indoor play', 'outdoor play',
        # column(s) that don't indicate the baby's actions
        'pump'
    ])
]
# %% convert date columns to datetime.datetime objects
df['start'] = df['start'].apply(util.my_date_conversion)
# %% if events don't have an end time, use the start time to represent it
df['end'] = df['end'].fillna(
    df['start'].apply(lambda d: d + dt.timedelta(seconds=constants.MINIMUM_EVENT_DURATION))
).apply(my_date_conversion)
# %%
df, event_column_dict = util.process_raw_data(df)
df = util.update_calculated_columns(df)
df = util.split_multi_day_events(df)
# extrapolate missing events
df = extrapolator.extrapolate(df)
# re-order columns and sort dataframe
df = df[[
    'type', 'start', 'end', 'date', 'start_time', 'end_time', 'duration', 'start condition',
    'start location', 'end condition', 'notes', 'legacy_duration'
]].sort_values('start')

# %% plot prep
BAR_HEIGHT = 0.8
NUM_WEEKS_TO_PLOT = 52
plot_date_filters = [
    constants.BIRTHDAY_DT,
    constants.BIRTHDAY_DT + dt.timedelta(days=366)
]
# number of days to be included in a row
# PLOT_ROW_SIZE = 7
PLOT_ROW_SIZE = 1
df['days_from_bday'] = (df['date'] - constants.BIRTHDAY).apply(lambda d: int(d.days))
df['col_num'] = (df['days_from_bday'] / PLOT_ROW_SIZE).astype(int)
df['row_num'] = df['days_from_bday'] - df['col_num'] * PLOT_ROW_SIZE
# df[['date', 'days_from_bday', 'col_num', 'row_num']].drop_duplicates().head(20)

# %%  T H E   P L O T
fig, ax = plt.subplots(
    # figsize=(30, 50)
    figsize=(20, BAR_HEIGHT * 2 * NUM_WEEKS_TO_PLOT)
)
# for date in date_range:
for ET in ['diaper', 'feed', 'sleep', 'birth', 'skin to skin', 'meds', 'bath', 'outdoor play', 'tummy time', 'indoor play', 'solids', 'brush teeth']:
# for ET in df['type'].unique():
    # define the "event data frame", used for plotting events of a certain color
    edf = df[
        (df['start'] >= plot_date_filters[0]) &
        (df['start'] < plot_date_filters[1]) &
        (df['date'].isin(days_with_overlap)) &
        (df['type'] == ET)
    ].sort_values('start', ascending=False)
    if ET in event_column_dict.keys():
        edf = edf.rename(columns=event_column_dict[ET])  # TODO: maybe remove this?
    if edf.shape[0] == 0:  # don't attempt to plot if there were no events of this type on this day
        continue

    for x in ['start', 'end']:
        # modify the start and end times to place multiple days on a row, by adding the number of
        #  seconds in a day multiplied by the number of day it is in the row.
        # For instance, if we wanted to fit 7 days on a row, then we would add a number of seconds
        #  to the start/end times for each event on that day that is equal to:
        #   7 * the number of seconds in a day
        edf[f'{x}_time'] += (edf['row_num'] * constants.HOURS_PER_DAY * constants.SECONDS_PER_HOUR)

    # plot bars
    plt.barh(
        y=(
            edf['start'].apply(util.my_date_conversion) -
            edf['row_num'].apply(lambda d: dt.timedelta(days=d))
        ).apply(lambda d: d.strftime('%Y-%m-%d')).values.reshape(len(edf)),
        width=edf['duration'].values.reshape(len(edf)),
        height=BAR_HEIGHT,
        left=edf['start_time'].values.reshape(len(edf)),
        label=ET,
        color=EVENT_COLOR_DICT[ET.lower()],
        alpha=0.5
    )

# tick_type = 'day_of_week'
tick_type = 'hour'
if tick_type == 'day_of_week':
    if PLOT_ROW_SIZE != 7:
        print(f'WARNING: cannot plot days of week unless PLOT_ROW_SIZE == 7 (currently {PLOT_ROW_SIZE})')
        print('continuing and setting tick_type = "hour"')
        tick_type = 'hour'
    dow_ticks = list(range(0, constants.HOURS_PER_DAY * PLOT_ROW_SIZE * constants.SECONDS_PER_HOUR, constants.HOURS_PER_DAY * constants.SECONDS_PER_HOUR))
    # dow_tick_labels = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue']
    dow_tick_labels = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    ax.set_xticks(dow_ticks)
    ax.set_xticklabels(dow_tick_labels)
    # OPTIONAL -- vertical lines at the start of each day
    for day_start_time in dow_ticks:
        plt.axvline(x=day_start_time, color='k', linestyle=':')
elif tick_type == 'hour':
    hour_step_size = 1
    hour_ticks = list(range(
        0, ((constants.HOURS_PER_DAY * PLOT_ROW_SIZE) + 1) * constants.SECONDS_PER_HOUR,
        hour_step_size * constants.SECONDS_PER_HOUR
    ))
    hour_tick_labels = [util.convert_num_seconds_to_time_of_day(x) for x in hour_ticks]
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_tick_labels)
# plt.rcParams.update({'font.size': 12})
plt.legend()
plt.show()
# %%
# %% find overlapping events
df = df.sort_values('start')
days_with_overlap = []
for idx in range(df.shape[0] - 1):
    event1 = df.iloc[idx]
    event2 = df.iloc[idx + 1]
    event1_end = event1['end']
    event2_start = event2['start']
    if event2_start < event1_end:
        overlap_time = event1_end - event2_start
        for i in (idx, idx + 1):
            print('\t'.join(
                # ' ' if np.isnan(df.iloc[i][c]) else
                str(df.iloc[i][c]) + ' ' * (max([len(c) for c in df['type'].unique()]) - len(str(df.iloc[i][c])))
                for c in [
                    'type', 'start', 'end', 'duration',
                    'start condition', 'end condition', 'start location'
                ]
            ))
        print('overlap:\t', overlap_time)
        print('* ' * 75)
        days_with_overlap.append(df.iloc[idx]['date'])
        # if idx > 1000:
        #     break
    break
print(len(days_with_overlap), 'days with overlap')
# %%



