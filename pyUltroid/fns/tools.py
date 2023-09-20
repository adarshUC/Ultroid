# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import json
import math
import os
import random
import re
import secrets
import ssl
from io import BytesIO
from json.decoder import JSONDecodeError
from traceback import format_exc

import requests

from .. import *
from ..exceptions import DependencyMissingError
from . import some_random_headers
from .helper import async_searcher, bash, run_async

try:
    import certifi
except ImportError:
    certifi = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image, ImageDraw, ImageFont = None, None, None
    LOGS.info("PIL not installed!")

from urllib.parse import quote, unquote

from telethon import Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo

if run_as_module:
    from ..dB.filestore_db import get_stored_msg, store_msg

try:
    import numpy as np
except ImportError:
    np = None

try:
    from telegraph import Telegraph
except ImportError:
    Telegraph = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# ~~~~~~~~~~~~~~~~~~~~OFOX API~~~~~~~~~~~~~~~~~~~~
# @buddhhu


async def get_ofox(codename):
    ofox_baseurl = "https://api.orangefox.download/v3/"
    releases = await async_searcher(
        ofox_baseurl + "releases?codename=" + codename, re_json=True
    )
    device = await async_searcher(
        ofox_baseurl + "devices/get?codename=" + codename, re_json=True
    )
    return device, releases


# ~~~~~~~~~~~~~~~JSON Parser~~~~~~~~~~~~~~~
# @buddhhu


def _unquote_text(text):
    return text.replace("'", unquote("%5C%27")).replace('"', unquote("%5C%22"))


def json_parser(data, indent=None, ascii=False):
    parsed = {}
    try:
        if isinstance(data, str):
            parsed = json.loads(str(data))
            if indent:
                parsed = json.dumps(
                    json.loads(str(data)), indent=indent, ensure_ascii=ascii
                )
        elif isinstance(data, dict):
            parsed = data
            if indent:
                parsed = json.dumps(data, indent=indent, ensure_ascii=ascii)
    except JSONDecodeError:
        parsed = eval(data)
    return parsed


# ~~~~~~~~~~~~~~~~Link Checker~~~~~~~~~~~~~~~~~


async def is_url_ok(url: str):
    try:
        return await async_searcher(url, head=True)
    except BaseException as er:
        LOGS.debug(er)
        return False


# ~~~~~~~~~~~~~~~~ Metadata ~~~~~~~~~~~~~~~~~~~~


async def metadata(file):
    out, _ = await bash(f'mediainfo "{_unquote_text(file)}" --Output=JSON')
    if _ and _.endswith("NOT_FOUND"):
        raise DependencyMissingError(
            f"'{_}' is not installed!\nInstall it to use this command."
        )
    data = {}
    _info = json.loads(out)["media"]["track"]
    info = _info[0]
    if info.get("Format") in ["GIF", "PNG"]:
        return {
            "height": _info[1]["Height"],
            "width": _info[1]["Width"],
            "bitrate": _info[1].get("BitRate", 320),
        }
    if info.get("AudioCount"):
        data["title"] = info.get("Title", file)
        data["performer"] = info.get("Performer") or udB.get_key("artist") or ""
    if info.get("VideoCount"):
        data["height"] = int(float(_info[1].get("Height", 720)))
        data["width"] = int(float(_info[1].get("Width", 1280)))
        data["bitrate"] = int(_info[1].get("BitRate", 320))
    data["duration"] = int(float(info.get("Duration", 0)))
    return data


# ~~~~~~~~~~~~~~~~ Attributes ~~~~~~~~~~~~~~~~


async def set_attributes(file):
    data = await metadata(file)
    if not data:
        return None
    if "width" in data:
        return [
            DocumentAttributeVideo(
                duration=data.get("duration", 0),
                w=data.get("width", 512),
                h=data.get("height", 512),
                supports_streaming=True,
            )
        ]
    ext = "." + file.split(".")[-1]
    return [
        DocumentAttributeAudio(
            duration=data.get("duration", 0),
            title=data.get("title", file.split("/")[-1].replace(ext, "")),
            performer=data.get("performer"),
        )
    ]


# ~~~~~~~~~~~~~~~~ Button stuffs ~~~~~~~~~~~~~~~


def get_msg_button(texts: str):
    btn = []
    for z in re.findall("\\[(.*?)\\|(.*?)\\]", texts):
        text, url = z
        urls = url.split("|")
        url = urls[0]
        if len(urls) > 1:
            btn[-1].append([text, url])
        else:
            btn.append([[text, url]])

    txt = texts
    for z in re.findall("\\[.+?\\|.+?\\]", texts):
        txt = txt.replace(z, "")

    return txt.strip(), btn


def create_tl_btn(button: list):
    btn = []
    for z in button:
        if len(z) > 1:
            kk = [Button.url(x, y.strip()) for x, y in z]
            btn.append(kk)
        else:
            btn.append([Button.url(z[0][0], z[0][1].strip())])
    return btn


def format_btn(buttons: list):
    txt = ""
    for i in buttons:
        a = 0
        for i in i:
            if hasattr(i.button, "url"):
                a += 1
                if a > 1:
                    txt += f"[{i.button.text} | {i.button.url} | same]"
                else:
                    txt += f"[{i.button.text} | {i.button.url}]"
    _, btn = get_msg_button(txt)
    return btn


# ~~~~~~~~~~~~~~~Saavn Downloader~~~~~~~~~~~~~~~
# @techierror


async def saavn_search(query: str):
    try:
        data = await async_searcher(
            url=f"https://saavn-api.vercel.app/search/{query.replace(' ', '%20')}",
            re_json=True,
        )
    except BaseException:
        data = None
                        input_file, name, remove=remove_old
                    )
            for exte in ["png", "jpg", "jpeg", "webp"]:
                if recycle_type(exte):
                    name = outname + "." + exte
                    return TgConverter.to_image(input_file, name, remove=remove_old)
        # Image to Something
        elif ext in ["jpg", "jpeg", "png", "webp"]:
            for extn in ["png", "webp", "ico"]:
                if recycle_type(extn):
                    img = Image.open(input_file)
                    name = outname + "." + extn
                    img.save(name, extn.upper())
                    if remove_old:
                        os.remove(input_file)
                    return name
            for extn in ["webm", "gif", "mp4"]:
                if recycle_type(extn):
                    name = outname + "." + extn
                    if extn == "webm":
                        input_file = await TgConverter.convert(
                            input_file,
                            convert_to="png",
                            remove_old=remove_old,
                        )
                    return await TgConverter.ffmpeg_convert(
                        input_file, name, remove=True if extn == "webm" else remove_old
                    )


def _get_value(stri):
    try:
        value = eval(stri.strip())
    except Exception as er:
        from .. import LOGS

        LOGS.debug(er)
        value = stri.strip()
    return value


def safe_load(file, *args, **kwargs):
    if isinstance(file, str):
        read = file.split("\n")
    else:
        read = file.readlines()
    out = {}
    for line in read:
        if ":" in line:  # Ignores Empty & Invalid lines
            spli = line.split(":", maxsplit=1)
            key = spli[0].strip()
            value = _get_value(spli[1])
            out.update({key: value or []})
        elif "-" in line:
            spli = line.split("-", maxsplit=1)
            where = out[list(out.keys())[-1]]
            if isinstance(where, list):
                value = _get_value(spli[1])
                if value:
                    where.append(value)
    return out


def get_chat_and_msgid(link):
    matches = re.findall("https:\\/\\/t\\.me\\/(c\\/|)(.*)\\/(.*)", link)
    if not matches:
        return None, None
    _, chat, msg_id = matches[0]
    if chat.isdigit():
        chat = int("-100" + chat)
    return chat, int(msg_id)


# --------- END --------- #
