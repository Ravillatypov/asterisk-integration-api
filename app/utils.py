import logging
from io import BytesIO
from pathlib import Path
from time import time

import ffmpeg
from aiohttp.client import ClientSession
from aiomisc.io import async_open
from mutagen.mp3 import MPEGInfo

from .settings import RECORDS_PATH, CONVERTED_RECORDS_PATH, RECORDS_UPLOAD_URL, RECORDS_UPLOAD_HEADERS


def get_full_path(file_name: str) -> str:
    *dirs, name = file_name.split('/')

    paths = [i.as_posix() for i in Path(RECORDS_PATH).glob(f'**/{name}')]
    paths = sorted(paths, key=lambda x: sum((1 for i in dirs if i in x)), reverse=True)

    if paths:
        return paths[0]

    return ''


def convert_record(source: str, call_id: str) -> str:
    if not source or not call_id or not Path(source).exists():
        return ''
    export_path = Path(CONVERTED_RECORDS_PATH).joinpath(f'{call_id}-{time()}.mp3')

    if export_path.exists():
        return export_path.as_posix()

    try:
        stream = ffmpeg.input(source)
        stream = ffmpeg.output(stream, export_path.as_posix())
        res = ffmpeg.run(stream)
        logging.info(f"call: {call_id}, result: {res}")
    except Exception as err:
        logging.warning(f'Error: {err}')

    return export_path.as_posix()


async def get_mp3_file_duration(path: str) -> int:
    if not path:
        return 0

    async with async_open(path, 'rb') as afp:
        data = await afp.read()

    try:
        return MPEGInfo(BytesIO(data)).length
    except Exception as err:
        logging.warning(f'Error on read mp3 file: {err}')

    return 0


async def upload_record(headers: dict, file_name: str) -> bool:
    if not RECORDS_UPLOAD_URL:
        return False

    async with async_open(file_name, 'rb') as afp:
        data = await afp.read()

    headers.update(RECORDS_UPLOAD_HEADERS)
    async with ClientSession(headers=headers) as ahttp:
        resp = await ahttp.put(RECORDS_UPLOAD_URL, data=data)
        return 199 < resp.status < 300
