from typing import List, Dict, Tuple

from pydantic import BaseSettings, Field


class BaseConfig(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class ATSConfig(BaseConfig):
    trunks: List[str] = Field([], env='TRUNK_NUMBERS')
    group_numbers: List[str] = Field([], env='GROUP_NUMBERS')
    context: str = Field('default', env='DEFAULT_CONTEXT')
    start_digit: str = Field('8', env='START_DIGIT')
    transport: str = Field('SIP', env='TRANSPORT')
    codes: Tuple[str] = Field(('7',), env='CITY_CODES')

    @property
    def codes_map(self) -> Dict[int, str]:
        return {len(i): i for i in self.codes}


class AmiConfig(BaseConfig):
    enabled: bool = Field(True, env='AMI_IS_ENABLED')
    ip: str = Field('127.0.0.1', env='IP')
    port: int = Field(5038, env='PORT')
    login: str = Field('', env='LOGIN')
    secret: str = Field('', env='SECRET')
    capture: List[str] = Field([], env='CAPTURE_EVENTS')


class RecordConfig(BaseConfig):
    enabled: bool = Field(True, env='RECORDS_IS_ENABLED')
    store_days: int = Field(30, env='RECORDS_STORE_DAYS')
    path: str = Field('/records', env='RECORDS_PATH')
    converted_path: str = Field('/records', env='CONVERTED_RECORDS_PATH')
    upload_url: str = Field('', env='RECORDS_UPLOAD_URL')
    upload_headers: Dict[str, str] = Field({}, env='RECORDS_UPLOAD_HEADERS')


class EventsConfig(BaseConfig):
    ws_url: str = Field('', env='WS_URL')
    ws_headers: Dict[str, str] = Field({}, env='WS_HEADERS')

    url: str = Field('', env='EVENTS_URL')
    headers: Dict[str, str] = Field({}, env='EVENTS_HEADERS')


class JWTConfig(BaseConfig):
    access_token_expire: int = Field(3600, env='JWT_ACCESS_EXPIRE')  # hour
    refresh_token_expire: int = Field(3600 * 24 * 14, env='JWT_REFRESH_EXPIRE')  # 14 days
    sig: str = Field('Wdfg5G5bNy}lsW4*', env='JWT_SIG')

    admin_token: str = Field('', env='ADMIN_TOKEN')
    tokens: Dict[str, List[int]] = Field({}, env='TOKENS')
    enabled: bool = Field(True, env='JWT_ENABLED')


class AppConfig(BaseConfig):
    env: str = Field('local', env='ENVIRONMENT')
    sentry_dsn: str = Field('', env='SENTRY_DSN')
    release: str = Field('local', env='RELEASE')
    data_path: str = Field('.', env='DATA_PATH')
    db_url: str = Field('sqlite://db.sqlite3', env='DB_URL')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    log_path: str = Field('.', env='LOG_PATH')
    web_port: int = Field(8000, env='WEB_PORT')

    ami: AmiConfig = Field(None)
    record: RecordConfig = Field(None)
    events: EventsConfig = Field(None)
    ats: ATSConfig = Field(None)
    jwt: JWTConfig = Field(None)

    @property
    def is_test(self) -> bool:
        return self.env == 'test'

    @property
    def is_prod(self) -> bool:
        return self.env == 'prod'

    @property
    def is_dev(self) -> bool:
        return self.env in ('local', 'dev')


app_config = AppConfig()
app_config.ami = AmiConfig()
app_config.record = RecordConfig()
app_config.events = EventsConfig()
app_config.ats = ATSConfig()
app_config.jwt = JWTConfig()
