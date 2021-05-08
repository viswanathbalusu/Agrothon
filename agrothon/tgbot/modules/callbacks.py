#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   callbacks.py
@Path    :   agrothon/tgbot/modules/
@Time    :   2021/05/8
@Author  :   Chandra Kiran Viswanath Balusu
@Version :   1.1.0
@Contact :   ckvbalusu@gmail.com
@Desc    :   Callbacks Module for telegram Keyboards
"""
import os
from sys import executable

import dotenv

from agrothon import LANG

from ..Client import AgroBot, filters
from ..helpers.apiserverhelper import *
from ..helpers.keyboards import *


@AgroBot.on_callback_query(
    filters.regex(pattern="^moisture|humidity|temperature|complete$")
)
async def callback_sensors(client, message):
    response = await sensor_get_latest()
    if response is not None:
        last_read = response["last_read"]
        up_at = response["updated_at"]
        if message.data == "moisture":
            await message.message.edit_text(
                text=LANG.MOISTURE_RESP.format(response["moisture"], up_at, last_read),
                reply_markup=sepkeyboard,
            )
        elif message.data == "humidity":
            await message.message.edit_text(
                text=LANG.HUMID_RESP.format(response["humidity"], up_at, last_read),
                reply_markup=sepkeyboard,
            )
        elif message.data == "temperature":
            await message.message.edit_text(
                text=LANG.TEMPE_RESP.format(response["temperature"], up_at, last_read),
                reply_markup=sepkeyboard,
            )
        elif message.data == "complete":
            pump_ = "ON" if response["pump_prediction"] else "OFF"
            await message.message.edit_text(
                text=LANG.COMPLETE_RESP.format(
                    response["moisture"],
                    response["humidity"],
                    response["temperature"],
                    pump_,
                    up_at,
                    last_read,
                ),
                reply_markup=sepkeyboard,
            )


@AgroBot.on_callback_query(filters.regex(pattern="^back|exit$"))
async def backcbq(client, message):
    if message.data == "back":
        await message.message.edit_text(text=LANG.MAIN_MENU, reply_markup=fieldkey)
    elif message.data == "exit":
        await message.message.delete()


@AgroBot.on_callback_query(
    filters.regex(pattern="^pumpstat|pumpon|pumpoff|refresh|bot$")
)
async def pumpque(client, message):
    if message.data == "pumpstat" or message.data == "refresh":
        response = await pump_get()
        if response is not None:
            if response["status"]:
                await message.message.edit_text(
                    text=LANG.PUMP_SWITCHED_ON.format(
                        response["by"], response["last_read"]
                    ),
                    reply_markup=pumponmenu,
                )
            else:
                await message.message.edit_text(
                    text=LANG.PUMP_SWITCHED_OFF.format(
                        response["by"], response["last_read"]
                    ),
                    reply_markup=pumpoffmenu,
                )
    elif message.data == "pumpon":
        response = await pump_post(True)
        if response is not None:
            await message.message.edit_text(
                text=LANG.PUMP_BTN_ON, reply_markup=pumpoffkey
            )
    elif message.data == "pumpoff":
        response = await pump_post(False)
        if response is not None:
            await message.message.edit_text(
                text=LANG.PUMP_BTN_OFF, reply_markup=pumponkey
            )
    elif message.data == "bot":
        response = await pump_post(True, by="AI Bot")
        if response is not None:
            await message.message.edit_text(
                text=LANG.BOT_ACTIVATED, reply_markup=backkey("pumpstat")
            )


def language_handler(mid, cid):
    with open(".setlangfile", "w") as r_file:
        r_file.truncate(0)
        r_file.write(f"{cid}\n{mid}")
    os.execl(executable, executable, "-m", "agrothon")


@AgroBot.on_callback_query(filters.regex(pattern="^eng|tel|tam|hin$"))
async def languages(client, message):
    if message.data == "eng":
        _lang = "english"
        os.environ["DEF_LANG"] = _lang
        dotenv.set_key("agrothon.env", "DEF_LANG", _lang)
        langmsg = await message.message.edit_text(
            text=LANG.LANG_CHANGED, reply_markup=backkey("lang")
        )
        language_handler(langmsg.message_id, langmsg.chat.id)
    elif message.data == "tel":
        _lang = "telugu"
        os.environ["DEF_LANG"] = _lang
        dotenv.set_key("agrothon.env", "DEF_LANG", _lang)
        langmsg = await message.message.edit_text(
            text=LANG.LANG_CHANGED, reply_markup=backkey("lang")
        )
        language_handler(langmsg.message_id, langmsg.chat.id)
    elif message.data == "tam":
        _lang = "tamil"
        os.environ["DEF_LANG"] = _lang
        dotenv.set_key("agrothon.env", "DEF_LANG", _lang)
        langmsg = await message.message.edit_text(
            text=LANG.LANG_CHANGED, reply_markup=backkey("lang")
        )
        language_handler(langmsg.message_id, langmsg.chat.id)
    elif message.data == "hin":
        _lang = "hindi"
        os.environ["DEF_LANG"] = _lang
        dotenv.set_key("agrothon.env", "DEF_LANG", _lang)
        langmsg = await message.message.edit_text(
            text=LANG.LANG_CHANGED, reply_markup=backkey("lang")
        )
        language_handler(langmsg.message_id, langmsg.chat.id)


@AgroBot.on_callback_query(filters.regex(pattern="^lang$"))
async def lang_change(client, message):
    await message.message.edit_text(text=LANG.SELECT_LANG, reply_markup=languageskey)


@AgroBot.on_callback_query(filters.regex(pattern="^restart$"))
async def restart_callback(client, message):
    restart_msg = await message.message.edit_text(text=LANG.RESTART)
    with open(".restartfile", "w") as r_file:
        r_file.truncate(0)
        r_file.write(f"{restart_msg.chat.id}\n{restart_msg.message_id}")
    os.execl(executable, executable, "-m", "agrothon")
