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

for raw_string in """2022-11-02 12:53:00 2022-11-02 20:12:00
2022-11-02 23:02:00 2022-11-02 23:08:00
2022-11-02 23:37:00 2022-11-02 23:59:59
2022-11-03 02:53:00 2022-11-03 04:29:00
2022-11-03 04:35:00 2022-11-03 06:00:00
2022-11-03 06:10:00 2022-11-03 09:10:00
2022-11-03 09:33:00 2022-11-03 12:58:00
2022-11-03 13:04:00 2022-11-03 16:34:00
2022-11-03 17:16:00 2022-11-03 19:37:00
2022-11-04 00:06:00 2022-11-04 01:18:00
2022-11-04 01:36:00 2022-11-04 03:00:00
2022-11-04 03:06:00 2022-11-04 04:49:00
2022-11-04 05:35:00 2022-11-04 07:08:00
2022-11-04 07:42:00 2022-11-04 11:18:00
2022-11-04 11:35:00 2022-11-04 12:16:00
2022-11-04 12:22:00 2022-11-04 12:51:00
2022-11-04 12:56:00 2022-11-04 13:12:00
2022-11-04 13:18:00 2022-11-04 14:03:00
2022-11-04 14:09:00 2022-11-04 17:45:00
2022-11-04 18:27:00 2022-11-04 19:32:00
2022-11-04 19:38:00 2022-11-04 20:59:00
2022-11-05 01:00:00 2022-11-05 03:58:00
2022-11-05 04:28:00 2022-11-05 07:32:00
2022-11-05 08:24:00 2022-11-05 11:22:00
2022-11-05 12:30:00 2022-11-05 14:44:00
2022-11-05 15:32:00 2022-11-05 17:40:00
2022-11-05 18:39:00 2022-11-05 20:23:00
2022-11-05 22:30:00 2022-11-05 23:35:00
2022-11-06 00:20:00 2022-11-06 01:26:00
2022-11-06 01:43:00 2022-11-06 03:12:00
2022-11-06 04:53:00 2022-11-06 07:15:00
2022-11-06 08:55:00 2022-11-06 12:05:00
2022-11-06 13:06:00 2022-11-06 14:57:00
2022-11-06 15:46:00 2022-11-06 17:28:00
2022-11-06 17:45:00 2022-11-06 21:10:00
2022-11-06 21:38:00 2022-11-06 23:01:00
2022-11-07 01:10:00 2022-11-07 02:23:00
2022-11-07 02:45:00 2022-11-07 03:19:00
2022-11-07 03:25:00 2022-11-07 04:00:00
2022-11-07 04:36:00 2022-11-07 06:00:00
2022-11-07 06:05:00 2022-11-07 07:00:00
2022-11-07 07:05:00 2022-11-07 09:00:00
2022-11-07 09:05:00 2022-11-07 09:40:00
2022-11-07 10:05:00 2022-11-07 10:43:00
2022-11-07 10:49:00 2022-11-07 13:19:00
2022-11-07 13:50:00 2022-11-07 15:46:00
2022-11-07 15:55:00 2022-11-07 18:22:00
2022-11-07 18:45:00 2022-11-07 21:13:00
2022-11-08 00:45:00 2022-11-08 02:40:00
2022-11-08 03:20:00 2022-11-08 04:51:00
2022-11-08 05:11:00 2022-11-08 07:30:00 
2022-11-08 07:46:00 2022-11-08 08:26:00
2022-11-08 08:32:00 2022-11-08 11:32:00
2022-11-08 11:40:00 2022-11-08 12:15:00
2022-11-08 12:20:00 2022-11-08 13:10:00 
2022-11-08 13:15:00 2022-11-08 13:57:00
2022-11-08 14:03:00 2022-11-08 15:17:00
2022-11-08 15:48:00 2022-11-08 18:51:00
2022-11-08 19:06:00 2022-11-08 22:03:00
2022-11-09 02:05:00 2022-11-09 04:50:00
2022-11-09 04:55:00 2022-11-09 07:09:00
2022-11-09 07:30:00 2022-11-09 09:17:00 
2022-11-09 10:01:00 2022-11-09 10:45:00 
2022-11-09 10:50:00 2022-11-09 12:22:00
2022-11-09 12:43:00 2022-11-09 15:04:00
2022-11-09 15:25:00 2022-11-09 16:08:00
2022-11-09 16:14:00 2022-11-09 17:05:00
2022-11-09 17:10:00 2022-11-09 20:05:00
2022-11-09 20:38:00 2022-11-09 22:34:00 
2022-11-10 02:43:00 2022-11-10 05:15:00 
2022-11-10 05:30:00 2022-11-10 07:38:00 
2022-11-10 07:56:00 2022-11-10 08:50:00
2022-11-10 09:30:00 2022-11-10 10:25:00 
2022-11-10 10:34:00 2022-11-10 12:52:00
2022-11-10 12:56:00 2022-11-10 14:38:00
2022-11-10 15:28:00 2022-11-10 17:59:00
2022-11-10 20:26:00 2022-11-10 21:06:00
2022-11-10 21:56:00 2022-11-10 23:40:00
2022-11-11 00:39:00 2022-11-11 01:30:00
2022-11-11 02:01:00 2022-11-11 02:40:00
2022-11-11 02:45:00 2022-11-11 03:27:00
2022-11-11 03:35:00 2022-11-11 06:30:00
2022-11-11 06:35:00 2022-11-11 09:05:00
2022-11-11 10:15:00 2022-11-11 11:08:00
2022-11-11 11:25:00 2022-11-11 13:27:00
2022-11-11 13:33:00 2022-11-11 14:25:00
2022-11-11 14:38:00 2022-11-11 17:10:00
2022-11-11 17:25:00 2022-11-11 18:14:00 
2022-11-11 18:42:00 2022-11-11 19:22:00
2022-11-11 23:13:00 2022-11-11 23:49:00
2022-11-12 00:38:00 2022-11-12 03:10:00
2022-11-12 03:39:00 2022-11-12 06:05:00
2022-11-12 06:36:00 2022-11-12 09:00:00
2022-11-12 09:10:00 2022-11-12 11:55:00 
2022-11-12 12:15:00 2022-11-12 12:37:00
2022-11-12 13:11:00 2022-11-12 14:18:00
2022-11-12 14:24:00 2022-11-12 15:01:00
2022-11-12 15:08:00 2022-11-12 18:08:00
2022-11-12 19:01:00 2022-11-12 22:13:00
2022-11-12 23:53:00 2022-11-12 23:59:59
2022-11-13 00:00:00 2022-11-13 00:38:00
2022-11-13 01:16:00 2022-11-13 02:55:00
2022-11-13 03:02:00 2022-11-13 06:01:00
2022-11-13 06:16:00 2022-11-13 09:04:00
2022-11-13 09:15:00 2022-11-13 12:00:00
2022-11-13 12:28:00 2022-11-13 15:04:00
2022-11-13 15:20:00 2022-11-13 16:53:00
2022-11-13 16:58:00 2022-11-13 17:52:00
2022-11-13 17:58:00 2022-11-13 18:15:00
2022-11-13 19:05:00 2022-11-13 21:28:00
2022-11-13 22:54:00 2022-11-13 23:59:59
2022-11-14 00:00:00 2022-11-14 00:23:00
2022-11-14 00:43:00 2022-11-14 02:10:00
2022-11-14 02:38:00 2022-11-14 05:10:00
2022-11-14 05:15:00 2022-11-14 06:00:00
2022-11-14 06:06:00 2022-11-14 08:09:00
2022-11-14 08:16:00 2022-11-14 09:26:00
2022-11-14 09:32:00 2022-11-14 11:00:00
2022-11-14 11:05:00 2022-11-14 13:25:00
2022-11-14 13:35:00 2022-11-14 14:08:00
2022-11-14 14:15:00 2022-11-14 16:20:00
2022-11-14 19:35:00 2022-11-14 22:02:00
2022-11-14 22:20:00 2022-11-14 23:59:59
2022-11-15 00:20:00 2022-11-15 00:27:00
2022-11-15 00:32:00 2022-11-15 02:20:00
2022-11-15 02:26:00 2022-11-15 03:04:00
2022-11-15 03:18:00 2022-11-15 05:45:00
2022-11-15 05:55:00 2022-11-15 08:45:00
2022-11-15 08:56:00 2022-11-15 11:20:00
2022-11-15 12:16:00 2022-11-15 14:30:00
2022-11-15 15:05:00 2022-11-15 17:20:00
2022-11-15 17:35:00 2022-11-15 20:50:00
2022-11-15 21:03:00 2022-11-15 23:59:59
2022-11-16 00:19:00 2022-11-16 01:27:00
2022-11-16 02:06:00 2022-11-16 04:05:00
2022-11-16 04:35:00 2022-11-16 07:10:00
2022-11-16 07:20:00 2022-11-16 10:00:00
2022-11-16 11:12:00 2022-11-16 12:51:00
2022-11-16 13:34:00 2022-11-16 16:30:00
2022-11-16 17:25:00 2022-11-16 19:57:00
2022-11-16 20:08:00 2022-11-16 22:34:00
2022-11-16 23:53:00 2022-11-16 23:59:59
2022-11-17 00:00:00 2022-11-17 00:25:00
2022-11-17 00:30:00 2022-11-17 02:00:00
2022-11-17 02:35:00 2022-11-17 05:00:00
2022-11-17 05:15:00 2022-11-17 08:07:00
2022-11-17 08:43:00 2022-11-17 10:00:00
2022-11-17 12:05:00 2022-11-17 13:03:00
2022-11-17 17:23:00 2022-11-17 18:40:00
2022-11-17 18:45:00 2022-11-17 20:22:00
2022-11-17 20:36:00 2022-11-17 21:13:00
2022-11-17 22:21:00 2022-11-17 23:59:59
2022-11-18 00:00:00 2022-11-18 00:44:00
2022-11-18 01:18:00 2022-11-18 04:30:00
2022-11-18 05:00:00 2022-11-18 07:30:00
2022-11-18 07:50:00 2022-11-18 09:12:00
2022-11-18 09:26:00 2022-11-18 10:33:00
2022-11-18 11:19:00 2022-11-18 12:19:00
2022-11-18 12:25:00 2022-11-18 13:44:00
2022-11-18 13:50:00 2022-11-18 16:25:00
2022-11-18 17:35:00 2022-11-18 20:06:00
2022-11-18 22:15:00 2022-11-18 23:59:59
2022-11-19 00:00:00 2022-11-19 00:17:00
2022-11-19 01:08:00 2022-11-19 03:50:00
2022-11-19 04:15:00 2022-11-19 06:19:00
2022-11-19 06:42:00 2022-11-19 08:30:00
2022-11-19 08:35:00 2022-11-19 11:47:00
2022-11-19 12:25:00 2022-11-19 15:20:00
2022-11-19 15:53:00 2022-11-19 18:40:00
2022-11-19 18:45:00 2022-11-19 21:00:00
2022-11-19 21:10:00 2022-11-19 22:00:00
2022-11-19 22:48:00 2022-11-19 23:59:59
2022-11-20 00:00:00 2022-11-20 01:42:00
2022-11-20 02:05:00 2022-11-20 04:32:00
2022-11-20 04:50:00 2022-11-20 06:40:00
2022-11-20 07:05:00 2022-11-20 09:43:00
2022-11-20 10:34:00 2022-11-20 12:19:00
2022-11-20 12:40:00 2022-11-20 14:40:00
2022-11-20 14:45:00 2022-11-20 15:40:00
2022-11-20 16:46:00 2022-11-20 18:40:00
2022-11-20 21:12:00 2022-11-20 22:38:00
2022-11-20 23:20:00 2022-11-20 23:59:59""".split('\n'):
    pass
    # start_time = dt.datetime.fromisoformat(raw_string[0:19])
    # end_time = dt.datetime.fromisoformat(raw_string[20:39])
    # artistic_liberties.append({**{
    #     'type': 'sleep', 'start': start_time, 'end': end_time
    # }, **other_columns})

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
