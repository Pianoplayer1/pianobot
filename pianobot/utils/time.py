from datetime import datetime, timedelta

def get_rounded_time(minutes: int):
    time = datetime.utcnow()
    interval = minutes * 60
    seconds = (time.replace(tzinfo = None) - time.min).seconds
    difference = (seconds + interval / 2) // interval * interval - seconds
    return str(time + timedelta(0, difference, -time.microsecond))
