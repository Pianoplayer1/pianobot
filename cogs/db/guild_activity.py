from datetime import datetime, timedelta
from logging import getLogger

from psycopg2.errors import UniqueViolation

from .connection import Connection

class Manager:
    def __init__(self, db: Connection):
        self._db = db
        self.guilds = ['Achte Shadow', 'Aequitas', 'Atlas Inc', 'Avicia', 'Blacklisted', 'Breadskate', 'Crystal Iris', 'Cyphrus Code', 'Eden', 'Emorians', 'Empire of Sindria', 'FlameKnights', 'Forever Twilight', 'ForsakenLaws', 'Fuzzy Spiders', 'Gabameno', 'Germany', 'Gopniks', 'Guardian of Wynn', 'HackForums', 'IceBlue Team', 'Idiot Co', 'Jasmine Dragon', 'Jeus', 'Kingdom Foxes', 'KongoBoys', 'Last Order', 'LittleBunny Land', 'Lux Nova', 'Nefarious Ravens', 'Nerfuria', 'Opus Maximus', 'Paladins United', 'Profession Heaven', 'Question Mark Syndicate', 'SICA Team', 'ShadowFall', 'Sins of Seedia', 'Skuc Nation', 'Syndicate of Nyx', 'TVietNam', 'Tartarus Wrath', 'The Aquarium', 'The Broken Gasmask', 'The Dark Phoenix', 'The Mage Legacy', 'The Simple Ones', 'TheNoLifes', 'Titans Valor', 'TruthSworD', 'Wheres The Finish', 'WynnFairyTail', 'busted moments']

    def get(self, guild: str, interval: int) -> dict[datetime: int]:
        sql = f'SELECT time, "{guild}" FROM "guildActivity" WHERE time > (CURRENT_TIMESTAMP - \'{interval} day\'::interval) ORDER BY time ASC;'
        result = self._db.query(sql)
        return {time: amount for time, amount in result}

    def add(self, data: dict[str: int]):
        time = datetime.utcnow()
        interval = 300
        seconds = (time.replace(tzinfo = None) - time.min).seconds
        difference = (seconds + interval / 2) // interval * interval - seconds
        rounded_time = str(time + timedelta(0, difference, -time.microsecond))

        columns = '", "'.join(data.keys())
        placeholders = '%s' + ', %s' * len(data)
        sql = f'INSERT INTO "guildActivity" (time, "{columns}") VALUES ({placeholders});'
        
        try:
            self._db.query(sql, rounded_time, *data.values())
        except UniqueViolation:
            getLogger('database').debug('Duplicate guild activity time')
