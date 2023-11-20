import datetime as dt
import numpy as np
import os
import pandas as pd
import time


def load_data():
    """Loads source data from local directory."""
    data_path = os.getcwd() + "\9df3f148-2d4f-4286-b0db-cc3e0b180668.csv"
    return pd.read_csv(data_path)


def my_date_conversion(d):
    """Converts an object into a datetime.datetime object.
    
    :param d: prospective datetime.datetime object (dt.date, dt.datetime, pd.Timestamp, str, np.datetime64)
    :return: datetime.datetime object
    """
    if isinstance(d, dt.datetime) or isinstance(d, dt.date):
        return d
    elif isinstance(d, pd.Timestamp):
        return pd.to_datetime(d)
    elif isinstance(d, np.datetime64):
        return dt.datetime.utcfromtimestamp(d.tolist() / 1e9)
    elif isinstance(d, str):
        for date_format in [
            '%Y-%m-%d %H:%M',
            '%m-%d-%Y %H:%M',
            '%Y-%m-%d',
            '%m-%d-%Y',
        ]:
            try:
                return dt.datetime.strptime(d.replace('/', '-').replace('T', ' '), date_format)
            except ValueError:
                pass
        raise ValueError(f"string value '{d}' is not a valid date format")
    else:
        raise ValueError(f"'{d}' ({type(d)}) cannot be converted to datetime.datetime")


def convert_num_seconds_to_time_of_day(t):
    """Given a number of seconds since midnight (integer), converts to the time of day it is."""
    return time.strftime('%H:%M', time.gmtime(t))


def process_raw_data(df):
    """Processes the raw input data and performs transformations including:
    * renaming all columns to be fully lowercase
    * removing event types that will not be plotted
    * 

    :param df: pandas.DataFrame containing raw data
    :param time_unit: str, unit of time to return the duration column in. May be "seconds",
        "minutes", "hours"
    :param minimum_duration: float, if an event has a duration of 0, it will be replaced with this
        duration value (in the time_unit provided)
    :return: df - processed data
             event_column_dict - dictionary mapping event types to dictionaries that maps names of
              columns in the raw dataframe to more appropriate names
    """
    # rename all columns to lowercase
    df = df.rename(columns={c: 'legacy_duration' if c == 'Duration' else c.lower() for c in df.columns})

    # remove event types that won't be covered
    df = df[
        ~df['type'].isin([
            # column(s) with very few entries
            # 'Brush teeth', 'Indoor play', 'Outdoor play',
            # column(s) that don't indicate Eleanor's actions
            'Pump'
        ])
    ]

    # if events don't have an end time, use the start time to represent it
    df['end'] = df['end'].fillna(df['start'])

    # convert date columns to datetime.datetime objects
    for c in ('start', 'end'):
        df[c] = df[c].apply(my_date_conversion)

    # create better column names for each type
    new_column_name_dict_list = {
        'Bath': {},
        'Brush teeth': {},
        'Diaper': {'legacy_duration': 'color', 'start condition': 'consistency', 'start location': 'issues', 'end condition': 'diaper contents'},
        'Feed': {'start condition': 'feed type', 'start location': 'delivery', 'end condition': 'amount'},
        'Indoor play': {},
        'Meds': {'start condition': 'amount', 'start location': 'name'},
        'Outdoor play': {},
        'Pump': {'start condition': 'amount'},
        'Skin to skin': {},
        'Sleep': {'start location': 'location'},
        'Solids': {'start condition': 'solids consumed', 'end condition': 'opinion'},
        'Tummy time': {},
    }
    event_column_dict = {}
    default_dict = {c: c for c in df.columns.tolist()}#['type', 'start', 'end', 'legacy_duration', 'start condition', 'start location', 'end condition', 'notes']
    for event_type in sorted(df['type'].unique()):
        column_dict = {**default_dict}
        new_column_name_dict = new_column_name_dict_list[event_type]
        for old_col, new_col in new_column_name_dict.items():
            column_dict[old_col] = new_col
        event_column_dict[event_type] = column_dict
    return df, event_column_dict


def split_multi_day_events(df):
    # split up entries that occur over two days (i.e. starts before midnight and ends after midnight)
    # for example: if an event lasts from 2023-07-01 23:55:00 -> 2023-07-02 00:10:00
    #  then it will be split into two new events with identical rows where
    #  one will last from 2023-07-01 23:55:00 -> 2023-07-01 23:59:59
    #  and the other from 2023-07-02 00:00:00 -> 2023-07-02 00:10:00
    #  Finally, the old row will be deleted.
    rows_to_drop = []
    rows_to_add = []
    for idx, row in df.iterrows():
        if row['start'].date() != row['end'].date():
            row1 = row.copy(deep=True)
            row1['end'] = dt.datetime(row['start'].year, row['start'].month, row['start'].day, 23, 59, 59)
            row2 = row.copy(deep=True)
            row2['start'] = dt.datetime(row['end'].year, row['end'].month, row['end'].day, 0, 0, 0)
            rows_to_drop.append(idx)
            rows_to_add.append(row1)
            rows_to_add.append(row2)
    # drop old rows, to prevent duplication
    for row in rows_to_add:
        df.loc[df.shape[0]] = row
    df = df.drop(rows_to_drop)
    # now that each event occurs on the same calendar date, add a "date" column
    df = df.assign(date=df['start'].apply(lambda d: my_date_conversion(d).date()))
    return df


def enhance_duration_column(df, time_unit='seconds', minimum_duration=0.0):
    """Calculate a better duration column, since "duration" in the original data is used for
    multiple purposes. The old "duration" column has already been renamed "legacy_duration".

    :param df: pandas.DataFrame containing raw data
    :param time_unit: str, unit of time to return the duration column in. May be "seconds",
        "minutes", "hours"
    :param minimum_duration: float, if an event has a duration of 0, it will be replaced with this
        duration value (in the time_unit provided)
    :return: df - processed data
    """
    time_unit = 'seconds'
    if time_unit == 'seconds':
        time_scale = 1.0
    elif time_unit == 'minutes':
        time_scale = 60.0
    elif time_unit == 'hours':
        time_scale = 60.0 * 60.0
    df = df.assign(duration=(df['end'] - df['start']).apply(
        lambda d: (minimum_duration if d.seconds == 0.0 else d.seconds) / time_scale
    ))
    return df
