import datetime as dt
import numpy as np
import pandas as pd

import util
import constants


def get_dict_of_other_columns():
    return {'legacy_duration': np.nan, 'start_condition': np.nan, 'start_location': np.nan, 'end_condition': np.nan, 'notes': 'extrapolation'}


def format_extrapolation(start, end, event_type='sleep'):
    return {**{'type': event_type, 'start': start, 'end': end}, **get_dict_of_other_columns()}


def add_birth_event(df):
    return combine_extrapolations_with_dataframe(df, [format_extrapolation(constants.BIRTHDAY_AND_TIME, constants.BIRTHDAY_AND_TIME, event_type='birth')])


def combine_extrapolations_with_dataframe(df, extrapolations):
    df = pd.concat([df, pd.DataFrame.from_records(extrapolations)])
    df = util.update_calculated_columns(df)
    return df


def extrapolate(df):
    """Extrapolates where sleep events would be, since J&A did not record all of them prior to 2022-12-24.
    These are interspersed between all other recorded events on those days (given enough space to do so).
    Also creates a "birth" event at 2022-11-02 12:48 PM."""
    df = add_birth_event(df)
    extrapolations = []
    for d in sorted(filter(lambda d: d < constants.FIRST_DATE_WITH_SLEEP_EVENTS, df['date'].unique())):
        ddf = df[df['date'] == d].sort_values('start')
        # for every day, add sleep events at the beginning and end of the day, since they were not recorded by J&A
        first_event = ddf['start'].min()
        last_event = ddf['end'].max()

        # if the first event of the day starts before the EXTRAPOLATION_MINUTE_THRESHOLD, don't add a sleep event before it
        # also, don't add a sleep event before date and time of birth
        if not (first_event.hour == 0 and first_event.minute <= constants.EXTRAPOLATION_MINUTE_THRESHOLD) and d != constants.BIRTHDAY:
            extrapolations.append(format_extrapolation(
                dt.datetime(first_event.year, first_event.month, first_event.day, 0, 0, 0),
                dt.datetime(first_event.year, first_event.month, first_event.day, first_event.hour, first_event.minute, 0)
                - dt.timedelta(minutes=constants.EXTRAPOLATION_MINUTE_BUFFER),
                event_type='sleep'
            ))

        # if the last event of the day ends within the EXTRAPOLATION_MINUTE_THRESHOLD of the end of the day, don't add a sleep event after it
        if not (last_event.hour == 23 and last_event.minute >= (60 - constants.EXTRAPOLATION_MINUTE_THRESHOLD)):
            extrapolations.append(format_extrapolation(
                dt.datetime(last_event.year, last_event.month, last_event.day, last_event.hour, last_event.minute, 0)
                + dt.timedelta(minutes=constants.EXTRAPOLATION_MINUTE_BUFFER),
                dt.datetime(last_event.year, last_event.month, last_event.day, 23, 59, 59),
                event_type='sleep'
            ))

        # intersperse sleep events between all other events
        for idx in range(ddf.shape[0] - 1):
            if (
                ddf.iloc[idx + 1]['start_time'] - ddf.iloc[idx]['end_time']
            ) > constants.EXTRAPOLATION_MINUTE_THRESHOLD * 60:
                extrapolations.append(format_extrapolation(
                    ddf.iloc[idx]['end'] + dt.timedelta(minutes=constants.EXTRAPOLATION_MINUTE_BUFFER),
                    ddf.iloc[idx + 1]['start'] - dt.timedelta(minutes=constants.EXTRAPOLATION_MINUTE_BUFFER),
                    event_type='sleep'
                ))
    df = combine_extrapolations_with_dataframe(df, extrapolations)
    return df
