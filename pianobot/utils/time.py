from datetime import datetime, timedelta, timezone

from corkus.objects import Player

def get_rounded_time(minutes: int):
    time = datetime.utcnow()
    interval = minutes * 60
    seconds = (time.replace(tzinfo = None) - time.min).seconds
    difference = (seconds + interval / 2) // interval * interval - seconds
    return str(time + timedelta(0, difference, -time.microsecond))

def format_last_seen(player: Player) -> list[int, str]:
    if player.online:
        days_offline = 0
        display_time = 'Online'
    else:
        diff = datetime.now(timezone.utc) - player.last_online
        days_offline = diff.days + (diff.seconds / 86400)
        value = days_offline
        unit = 'day'
        if value < 1:
            value *= 24
            unit = 'hour'
            if value < 1:
                value *= 60
                unit = 'minute'
        if round(value) != 1:
            unit += 's'
        display_time = f'{round(value)} {unit}'
    return display_time
