""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
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


def in_correct_server() -> Callable[[T], T]:

    async def predicate(ctx: commands.Context):

        if ctx.guild.id not in [int(os.environ.get("guild_id")),] and not isinstance(ctx.channel, discord.channel.DMChannel):
            raise WrongChannel("You are only able to use this command in the main server, use /invite to get an invite")
        return True
    
    return commands.check(predicate)


def not_in_dm() -> Callable[[T], T]:

    async def predicate(ctx: commands.Context):

        if isinstance(ctx.channel, discord.channel.DMChannel):
            raise WrongChannel("You cannot use this command in dm, use /invite to get an invite")
        return True
    
    return commands.check(predicate)


def cost_nword(cost: int) -> Callable[[T], T]:

    async def predicate(ctx: commands.Context):
        nword_count = await db_manager.get_nword_count(ctx.author.id)
        # Geen berichten
        if len(nword_count) == 0 or int(nword_count[0][0]) == 0:
            exact_count = 0
        
        # error
        elif nword_count[0] == -1:
            raise Exception("Could not fetch nword count!")
        
        else:
            exact_count = int(nword_count[0][0])

        # user heeft niet genoeg nwords
        if exact_count < cost:
            raise MissingNwords(exact_count, cost)
        
        # update nword count
        await db_manager.set_nword_count(ctx.author.id, exact_count-cost)

        return True
    
    return commands.check(predicate)