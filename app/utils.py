from datetime import datetime
from io import BytesIO
from pathlib import Path
from time import time
from typing import Union

import ffmpeg
from aiohttp.client import ClientSession
from aiomisc.io import async_open
from mutagen.mp3 import MPEGInfo

from .config import app_config
from .misc.logging import get_logger

logger = get_logger('app')


def get_full_path(file_name: str) -> str:
    *dirs, name = file_name.split('/')

    paths = [i.as_posix() for i in Path(app_config.record.path).glob(f'**/{name}')]
    paths = sorted(paths, key=lambda x: sum((1 for i in dirs if i in x)), reverse=True)

    if paths:
        return paths[0]

    return ''


def convert_record(source: str, call_id: str) -> str:
    if not source or not call_id or not Path(source).exists():
        return ''
    export_path = Path(app_config.record.converted_path).joinpath(f'{call_id}-{time()}.mp3')

    if export_path.exists():
        return export_path.as_posix()

    try:
        stream = ffmpeg.input(source)
        stream = ffmpeg.output(stream, export_path.as_posix())
        res = ffmpeg.run(stream)
        logger.info(f'call: {call_id}, result: {res}')
    except Exception as err:
        logger.warning(f'Error: {err}')

    return export_path.as_posix()


async def get_mp3_file_duration(path: str) -> int:
    if not path:
        return 0

    async with async_open(path, 'rb') as afp:
        data = await afp.read()

    try:
        return MPEGInfo(BytesIO(data)).length
    except Exception as err:
        logger.warning(f'Error on read mp3 file: {err}')

    return 0


async def upload_record(headers: dict, file_name: str) -> bool:
    if not app_config.record.enabled or not app_config.record.upload_url:
        return False

    async with async_open(file_name, 'rb') as afp:
        data = await afp.read()

    headers.update(app_config.record.upload_headers)
    async with ClientSession(headers=headers) as ahttp:
        resp = await ahttp.put(app_config.record.upload_url, data=data)
        return 199 < resp.status < 300


def add_city_code(number: str) -> str:
    ln = 11 - len(number)
    return app_config.ats.codes_map.get(ln, '') + number


def convert_datetime(dt: datetime) -> Union[None, str]:
    if isinstance(dt, datetime):
        return dt.isoformat(timespec='seconds')
    return None
