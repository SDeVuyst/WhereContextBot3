""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import json
import os
from typing import Callable, TypeVar

from discord.ext import commands

from exceptions import *
from helpers import db_manager

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """

    async def predicate(context: commands.Context) -> bool:
        if str(context.author.id) not in list(os.environ.get("owners").split(",")):
            raise UserNotOwner
        return True

    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is blacklisted.
    """

    async def predicate(context: commands.Context) -> bool:
        if await db_manager.is_blacklisted(context.author.id):
            raise UserBlacklisted
        return True

    return commands.check(predicate)


def in_audio_command_channel() -> Callable[[T], T]:

    async def predicate(ctx: commands.Context):
        if ctx.channel.id not in [1114464141508345906, 727511733970665493]:
            raise WrongChannel("Only able to play in #out-of-context-game or #music-bot")
        return True
    
    return commands.check(predicate)
