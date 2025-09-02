from datetime import datetime, timedelta, date as dt_date


def current_date():
    return dt_date.today().strftime("%Y-%m-%d")
