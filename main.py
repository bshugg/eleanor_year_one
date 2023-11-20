# TODO (2023-11-15)
# * fill in missing "sleep" events
# * get the plot to show dates in order
# TODO (2023-11-19)
# * add birth event
# * handle overlapping events in aesthetically pleasing way
# * define color pallets (ask J & A)
# * make alternative formats for y-axis ticks (e.g. "Nov 2" instead of YYYY-MM-DD)
# * consider removing the min_hour/max_hour stuff

# %% imports
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import util

# constants
BIRTHDAY = dt.date(2022, 11, 2)
BIRTHDAY_DT = dt.datetime(BIRTHDAY.year, BIRTHDAY.month, BIRTHDAY.day)
BIRTHDAY_AND_TIME = dt.datetime(BIRTHDAY.year, BIRTHDAY.month, BIRTHDAY.day, 12, 48, 00)
SECONDS_PER_HOUR = 60 * 60
HOURS_PER_DAY = 24
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

# %% load data and process initial data
DF_ORIG = util.load_data()
df = DF_ORIG.copy(deep=True)
MINIMUM_DURATION = 5.0 * 60.0  # five minutes
df, event_column_dict = util.process_raw_data(df)
df = util.split_multi_day_events(df)
df = util.calculate_date_column(df)
df = util.calculate_time_columns(df)

# %% fill in missing events with some artistic liberties
other_columns = {'legacy_duration': np.nan, 'start_condition': np.nan, 'start_location': np.nan, 'end_condition': np.nan, 'notes': 'artistic liberty'}
artistic_liberties = [{**{'type': 'birth', 'start': BIRTHDAY_AND_TIME, 'end': BIRTHDAY_AND_TIME}, **other_columns}]
df = pd.concat([df, pd.DataFrame.from_records(artistic_liberties)])
df = util.calculate_date_column(df)
df = util.calculate_time_columns(df)


# %%
for d in sorted(df['date'].unique()):
    ddf = df[df['date'] == d].sort_values('start')
    if d < dt.date(2022, 12, 24):
        # intersperse sleep events
        # define threshold at which, if this many minutes are empty between events,
        #  we want to add a sleep event
        MINUTE_THRESHOLD = 15
        MINUTE_BUFFER = 5
        for idx in range(ddf.shape[0] - 1):
            time_between_events = ddf.iloc[idx + 1]['start_time'] - ddf.iloc[idx]['end_time']
            if time_between_events > MINUTE_THRESHOLD * 60:
                artistic_liberties.append({**{
                    'type': 'sleep',
                    'start': ddf.iloc[idx]['end'] + dt.timedelta(minutes=MINUTE_BUFFER),
                    'end': ddf.iloc[idx + 1]['start'] - dt.timedelta(minutes=MINUTE_BUFFER),
                }, **other_columns})
    # for every day, add "sleep" events at the beginning and end of the day
    first_event = ddf['start'].min()
    last_event = ddf['end'].max()
    if not (first_event.hour == 0 and first_event.minute <= MINUTE_THRESHOLD) and d != BIRTHDAY:
        artistic_liberties.append({**{
            'type': 'sleep',
            'start': dt.datetime(first_event.year, first_event.month, first_event.day, 0, 0, 0),
            'end': dt.datetime(first_event.year, first_event.month, first_event.day, first_event.hour, first_event.minute, 0) - dt.timedelta(minutes=1),
        }, **other_columns})
    if not (last_event.hour == 23 and last_event.minute >= 60 - MINUTE_THRESHOLD):
        artistic_liberties.append({**{
            'type': 'sleep',
            'start': dt.datetime(last_event.year, last_event.month, last_event.day, last_event.hour, last_event.minute, 0) + dt.timedelta(minutes=1),
            'end': dt.datetime(last_event.year, last_event.month, last_event.day, 23, 59, 59),
        }, **other_columns})
# %%
df = pd.concat([df, pd.DataFrame.from_records(artistic_liberties)])
df = util.calculate_date_column(df)
df = util.calculate_time_columns(df)

# %% FINAL PROCESSING
df = util.enhance_duration_column(df, time_unit='seconds', minimum_duration=MINIMUM_DURATION)
# re-order columns and sort dataframe
df = df[[
    'type', 'start', 'end', 'date', 'start_time', 'end_time', 'duration', 'start condition',
    'start location', 'end condition', 'notes', 'legacy_duration'
]].sort_values('start')

# %% plot prep
BAR_HEIGHT = 0.8
NUM_WEEKS_TO_PLOT = 8
plot_date_filters = [BIRTHDAY_DT, BIRTHDAY_DT + dt.timedelta(days=7 * NUM_WEEKS_TO_PLOT)]
# plot_date_filters = [
#     BIRTHDAY_DT + dt.timedelta(days=n),
#     BIRTHDAY_DT + dt.timedelta(days=n + 1)
# ]
# date_range = sorted(df[(df['start'] >= plot_date_filters[0]) & (df['start'] < plot_date_filters[1])]['date'].unique())

# minimum and maximum hours of the day covered by the data. used to bound the plot
min_hour = HOURS_PER_DAY
max_hour = 0

# number of days to be included in a row
# PLOT_ROW_SIZE = 7
PLOT_ROW_SIZE = 1
df['days_from_bday'] = (df['date'] - BIRTHDAY).apply(lambda d: int(d.days))
df['col_num'] = (df['days_from_bday'] / PLOT_ROW_SIZE).astype(int)
df['row_num'] = df['days_from_bday'] - df['col_num'] * PLOT_ROW_SIZE
# df[['date', 'days_from_bday', 'col_num', 'row_num']].drop_duplicates().head(20)

# %%  T H E   P L O T
fig, ax = plt.subplots(
    # figsize=(30, 50)
    figsize=(20, BAR_HEIGHT * 2 * NUM_WEEKS_TO_PLOT)
)
# for date in date_range:
for ET in ['diaper', 'feed', 'sleep', 'birth', 'skin to skin', 'meds', 'bath', 'outdoor play', 'tummy time', 'indoor play', 'solids', 'brush teeth']:#df['type'].unique():
    # define the "event data frame", used for plotting events of a certain color
    edf = df[
        # (df['date'] == date) &
        (df['start'] >= plot_date_filters[0]) &
        (df['start'] < plot_date_filters[1]) &
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

# tick_type = 'day_of_week'
tick_type = 'hour'
if tick_type == 'day_of_week':
    if PLOT_ROW_SIZE != 7:
        print(f'WARNING: cannot plot days of week unless PLOT_ROW_SIZE == 7 (currently {PLOT_ROW_SIZE})')
        print('continuing and setting tick_type = "hour"')
    dow_ticks = list(range(0, HOURS_PER_DAY * PLOT_ROW_SIZE * SECONDS_PER_HOUR, HOURS_PER_DAY * SECONDS_PER_HOUR))
    # dow_tick_labels = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue']
    dow_tick_labels = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    ax.set_xticks(dow_ticks)
    ax.set_xticklabels(dow_tick_labels)
    # OPTIONAL -- vertical lines at the start of each day
    for day_start_time in dow_ticks:
        plt.axvline(x=day_start_time, color='k', linestyle=':')
elif tick_type == 'hour':
    if max_hour <= min_hour:  # last minute catch-all
        print(f'||| WARNING |||\nmax hour {max_hour} should be > min hour {min_hour}')
        min_hour, max_hour = 0, HOURS_PER_DAY
    hour_step_size = 1
    # hour_step_size = 3
    # hour_step_size = 6
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
# plt.rcParams.update({'font.size': 12})
plt.legend()
plt.show()










# %%
# %%
# %%
n = 0
# %% ARTISTIC LIBERTY ASSISTER
my_artistic_date = pd.date_range(BIRTHDAY, dt.date(2022, 12, 24))[n]
fig, ax = plt.subplots(
    figsize=(20, 0.8 * 2 * 1)
)
for ET in df['type'].unique():
    # define the "event data frame", used for plotting events of a certain color
    edf = df[
        (df['date'] == my_artistic_date) &
        (df['type'] == ET)
    ].sort_values('start', ascending=False)
    if edf.shape[0] == 0:  # don't attempt to plot if there were no events of this type on this day
        continue
    for x in ['start', 'end']:
        edf[f'{x}_time'] = (
            edf[x] - edf['start'].apply(lambda d: dt.datetime(d.year, d.month, d.day))
        ).apply(lambda d: d.seconds)
    plt.barh(
        y=edf['start'].apply(lambda d: util.my_date_conversion(d).strftime('%Y-%m-%d')),
        width=edf['duration'],
        # height=0.8,
        left=edf['start_time'],
        label=ET,
        color=EVENT_COLOR_DICT[ET.lower()],
        alpha=0.5
    )
hour_step_size = 1
hour_ticks = list(range(0, (24 + 1) * SECONDS_PER_HOUR, hour_step_size * SECONDS_PER_HOUR))
hour_tick_labels = [util.convert_num_seconds_to_time_of_day(x) for x in hour_ticks]# * PLOT_ROW_SIZE
ax.set_xticks(hour_ticks)
ax.set_xticklabels(hour_tick_labels)
print(df[df['date'] == my_artistic_date][['type', 'start', 'end']].sort_values('start'))
n += 1
plt.legend()
plt.show()
# %%
# %%
# %%
# %%
# %%
# %%
