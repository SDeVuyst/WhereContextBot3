"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import json
import logging
import os
import platform
import random
import sys
import psycopg2

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from helpers import db_manager
import exceptions


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = Bot(
    command_prefix='',
    intents=intents,
    help_command=None,
)

bot.defaultColor = 0xF4900D
bot.errorColor = 0xE02B2B
bot.succesColor = 0x39AC39

bot.loaded = set()
bot.unloaded = set()
# Setup both of the loggers


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
bot.logger = logger


def init_db():
    with psycopg2.connect(
        os.environ.get("DATABASE_URL"), sslmode='require'
    ) as con:
        
        with con.cursor() as cursor:

            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
            ) as file:
                cursor.execute(file.read())

    bot.logger.info(f"initializing db'")


@bot.event
async def on_ready() -> None:
    """
    The code in this event is executed when the bot is ready.
    """
    bot.logger.info(f"Logged in as {bot.user.name}")
    bot.logger.info(f"discord.py API version: {discord.__version__}")
    bot.logger.info(f"Python version: {platform.python_version()}")
    bot.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    bot.logger.info("-------------------")
    status_task.start()

@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot.
    """
    amount = await db_manager.messages_in_ooc()
    statuses = ["Ora et Labora", f"{amount} berichten in outofcontext", "met ba zijn gevoelens", "with Astolfo", "Minecraft", "with gible z'n ma", "with grom z'n ma", "🚨 Scanning for n-words 🚨"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message

    :param message: The message that was sent.
    """
    if message.author == bot.user or message.author.bot:
        return
    
    # stuur dm naar solos on prive command
    
    if message.guild is None:
        # solos user object
        owner = int(list(os.environ.get("owners").split(","))[0])
        user = await bot.fetch_user(owner)
        await user.send(content=f"{message.author.display_name} sent: {message.content}")

        for att in message.attachments:
            await user.send(content=att.url)
        


    await findNWord(message)
    # await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    bot.logger.info(f"{member.id} joined the server!")

    # add member role
    member_role = discord.utils.get(member.guild.roles, id=753959093185675345)
    bot.logger.info(f"adding member role")
    await member.add_roles(member_role)

    roles = {
        # yachja                   minecraft           cultured            perms               yachja
        733845345225670686: [739212609248690248, 740301828071358738, 756224050237538325, 1119328394568548402],
        # gible                    gent                minecraft
        559715606014984195: [1024341053786038332, 739212609248690248],
        # arno                     homeless          sugardaddy          gent                minecraft         
        273503117348306944: [801146953470967809, 827108224485294100, 1024341053786038332, 739212609248690248],
        # pingy                    fortnut           spooderman          genshin             waifu bot             gent                minecraft           cultured            cringe             titanfood           perms
        464400950702899211: [946064405597138994, 918990342840275035, 817107290708639774, 778688939623710770, 1024341053786038332, 739212609248690248,740301828071358738, 836973694630887455, 787665548506955776, 756224050237538325],
        # solos                indian tech god           gent              spooderman           wcb3                minecraft       not cultured         owner               perms               meng              cummaster
        462932133170774036: [1079432980038172805, 1024341053786038332, 918990342840275035, 1119600252228489296, 739212609248690248, 805130046414127126, 799385460677804043, 756224050237538325, 777956016033103872, 851467556040474624]
    }

    

    if member.id in roles:
        roles_to_add = roles.get(member.id)
        for role_id in roles_to_add:
            try:
                new_role = discord.utils.get(member.guild.roles, id=role_id)
                bot.logger.info(f"adding {role_id}")
                await member.add_roles(new_role)
            except:
                bot.logger.warning(f"role {role_id} not found")

        

    await member.send('Added your roles back!')



@bot.event
async def on_command_completion(context: Context) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed.

    :param context: The context of the command that has been executed.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        bot.logger.info(
            f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
        )
    else:
        bot.logger.info(
            f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
        )


# check for inactivity in voice channel
@bot.event
async def on_voice_state_update(member, before, after) -> None:
    
    if not member.id == bot.user.id:
        return

    elif before.channel is None:
        voice = after.channel.guild.voice_client
        # time = 0
        while True:
            await asyncio.sleep(5)
            if len(voice.channel.members) == 1:
                bot.logger.info("disconnecting bot due to inactivity")
                await voice.disconnect()

            # time = time + 1
            # if voice.is_playing() and not voice.is_paused():
            #     time = 0
            # if time == 600:
            #     await voice.disconnect()
            if not voice.is_connected():
                break


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error.

    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=bot.errorColor,
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.not_blacklisted() check in your command, or you can raise the error by yourself.
        """
        embed = discord.Embed(
            description="You are blacklisted from using the bot!", color=bot.errorColor
        )
        await context.send(embed=embed, ephemeral=True)
        if context.guild:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute a command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is blacklisted from using the bot."
            )
        else:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute a command in the bot's DMs, but the user is blacklisted from using the bot."
            )
    elif isinstance(error, exceptions.UserNotOwner):
        """
        Same as above, just for the @checks.is_owner() check.
        """
        embed = discord.Embed(
            description="You are not the owner of the bot!", color=bot.errorColor
        )
        await context.send(embed=embed, ephemeral=True)
        if context.guild:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
            )
        else:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
            )
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description="You are missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to execute this command!",
            color=bot.errorColor,
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            description="I am missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to fully perform this command!",
            color=bot.errorColor,
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="You are missing some required arguments!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=bot.errorColor,
        )
        await context.send(embed=embed)

    elif isinstance(error, exceptions.WrongChannel):
        embed = discord.Embed(
            title="Wrong channel!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=bot.errorColor,
        )
        await context.send(embed=embed, ephemeral=True)

    else:
        # embed = discord.Embed(
        #     title="Error!",
        #     # We need to capitalize because the command arguments have no capital letter in the code.
        #     description=str(error).capitalize(),
        #     color=bot.errorColor,
        # )
        # await context.send(embed=embed)
        raise error


async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                bot.logger.info(f"Loaded extension '{extension}'")
                bot.loaded.add(extension)

            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                bot.logger.error(f"Failed to load extension {extension}\n{exception}")
                bot.unloaded.add(extension)


async def findNWord(message):
    content = message.content.replace(" ", "").replace("\n", "").lower()
    
    # ik heb dit niet zelf getypt lol 💀
    toCheck = ["negro","squigga","squiga","nigger","neger","nigga","nigglet","niglet", "niger","nigr","niggr","nikka","niglonian", "🇳 🇮 🇬 🇬 🇦", "nigge"]

    for c in toCheck:
        for _ in range(content.count(c)):
            await db_manager.increment_or_add_nword(m.author.id)
            
    

init_db()
asyncio.run(load_cogs())
bot.run(os.environ.get("token"))

