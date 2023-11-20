import datetime as dt

BIRTHDAY = dt.date(2022, 11, 2)
BIRTHDAY_DT = dt.datetime(BIRTHDAY.year, BIRTHDAY.month, BIRTHDAY.day)
BIRTHDAY_AND_TIME = dt.datetime(BIRTHDAY.year, BIRTHDAY.month, BIRTHDAY.day, 12, 48, 00)

SECONDS_PER_HOUR = 60 * 60
HOURS_PER_DAY = 24

# when interspersing events, if fewer minutes than this are between the events, do not insert an event between them
EXTRAPOLATION_MINUTE_THRESHOLD = 15

# the buffer to place between events, when extrapolating new ones
EXTRAPOLATION_MINUTE_BUFFER = 5

# all dates before this don't have sleep events, so they must be extrapolated
FIRST_DATE_WITH_SLEEP_EVENTS = dt.date(2022, 12, 24)
