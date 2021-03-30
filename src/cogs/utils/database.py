import psycopg2
import yaml


class Database:
    def __init__(self) -> None:
        with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        self.db = config.get('database', {})

        connection = psycopg2.connect(
            host=self.db['host'],
            dbname=self.db['dbname'],
            user=self.db['username'],
            password=self.db['password']
        )

        self.cursor = connection.cursor()


class Guild(Database):
    def __init__(self, id: int) -> None:
        super().__init__()
        self.id = id

    def get_all(self):
        self.cursor.execute('SELECT * FROM guild WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    @property
    def prefix(self) -> str:
        self.cursor.execute('SELECT prefix FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    @property
    def locale(self) -> str:
        self.cursor.execute('SELECT locale FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    def is_oauth(self) -> bool:
        self.cursor.execute('SELECT oauth FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    def is_country_whitelisted(self, country_code: str) -> bool:
        self.cursor.execute('SELECT whitelisted_countries FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response and country_code in response:
            return True
