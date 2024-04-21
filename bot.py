"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import logging
import os
import platform
import random
import psycopg2
import time
import discord
import requests
from bs4 import BeautifulSoup

from discord.ext import tasks
from discord.ext.commands import AutoShardedBot
from discord import Webhook
import aiohttp

import embeds
from helpers import WordFinder, db_manager, ArtBuilder
import exceptions

from datetime import datetime, timedelta

from cogs.general import DynamicVotesButton

intents = discord.Intents.all()

bot = AutoShardedBot(
    command_prefix='',
    intents=intents,
    help_command=None,
)

FORTNITE_MAPS = {
    "Naruto Box PVP": {
        "mapcode": "3216-2522-9844",
    },
    "📦STARWARS BOX PVP🔥": {
        "mapcode": "1630-9217-6519",
    }
}

WEBHOOK_URLS_FORTNITE = [
    "https://discord.com/api/webhooks/1218834508703596554/p8SOyOe7jRZ8Ed0o5OzUQ5XuCqLznr4V1y4dqfowXvLT1RYqnlRtUZRBi-0623Fq6QcC",
    "https://discord.com/api/webhooks/1224272410854035496/YmJPolsS5LCo1EiH-cl9YM5wQ3Y5kk78ZpeIzoA2i-vM45ZSxSe6V2s7vYnIawdXx9fT"
]

bot.loaded = set()
bot.unloaded = set()

bot.status_manual = None
bot.gif_prohibited = []

bot.quote_gestuurd = False

def save_ids_func(cmds):
    """Saves the ids of commands

    Args:
        cmds (Command)
    """
    for cmd in cmds:
        try:
            if cmd.guild_id is None:  # it's a global slash command
                bot.tree._global_commands[cmd.name].id = cmd.id
            else:  # it's a guild specific command
                bot.tree._guild_commands[cmd.guild_id][cmd.name].id = cmd.id
        except:
            pass

bot.save_ids = save_ids_func

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
    time.sleep(30)
    with psycopg2.connect(
        host='192.168.86.200', dbname='pg_wcb3', user=os.environ.get('POSTGRES_USER'), password=os.environ.get('POSTGRES_PASSWORD')
    ) as con:
        
        with con.cursor() as cursor:

            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
            ) as file:
                cursor.execute(file.read())

    bot.logger.info(f"initializing db")


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

    await init_fortnite_player_peak()

    # start tasks
    try:
        check_fortnite_player_peak.start()
        status_task.start()
        check_remindme.start()
        check_gif_unban.start()
        check_quote_send.start()

    except Exception as e:
        bot.logger.warning(e)


    cmds = await bot.tree.sync()
    bot.save_ids(cmds)


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot.
    """

    # check if someone used the status command
    if bot.status_manual is not None:
        # longer than 1 hour ago
        time_diff = datetime.now() - bot.status_manual 
        if time_diff.total_seconds() > 3600:
            bot.status_manual = None

    if bot.status_manual is None:
        amount = await db_manager.messages_in_ooc()
        statuses = [
            f"📈 {amount} berichten in Out-of-Context!",
            f"🦾 The Art Update out now!",
            f'🦮 /help',
        ]

        picked_status = random.choice(statuses)
        await bot.change_presence(activity=discord.CustomActivity(name=picked_status))


@tasks.loop(seconds=30)
async def check_gif_unban():
    ok_list = []
    for user, t in bot.gif_prohibited:

        # not longer than 15 minutes ago
        time_diff = datetime.now() - t
        if time_diff.total_seconds() < 900:
            ok_list.append((user, t))
    
    bot.gif_prohibited = ok_list


@tasks.loop(seconds=30)
async def check_remindme():

    # krijg reminders uit db
    reminders = await db_manager.get_reminders()

    # Geen berichten
    if len(reminders) == 0: return
    # error
    elif reminders[0] == -1:
        bot.logger.warning(f"Could not fetch reminders: {reminders[1]}")

    else:
        # check elke reminder
        for reminder in reminders:
            id, user_id, subject, time = tuple(reminder)

            # reminder is in verleden, dus stuur bericht
            if datetime.strptime(time, '%d/%m/%y %H:%M:%S') - timedelta(hours=2) < datetime.now():

                # stuur reminder
                user = await bot.fetch_user(int(user_id))
                embed = embeds.DefaultEmbed(
                    "⏰ Reminder!", f"```{subject}```", user=user
                )

                await user.send(embed=embed)

                # verwijder reminder uit db
                succes = await db_manager.delete_reminder(id)
                if succes:
                    bot.logger.info(f"Sent out a reminder ({subject})")
                else:
                    bot.logger.warning("could not delete reminder")


@tasks.loop(seconds=60)
async def check_fortnite_player_peak():
    for naam, map_info in FORTNITE_MAPS.items():
        peak = await get_fortnite_player_peak(map_info["mapcode"])
        
        if peak > map_info["max"]:
            map_info["max"] = peak
            FORTNITE_MAPS[naam] = map_info

            # notify user
            logger.info(f"new {FORTNITE_MAPS[naam]} max player count found")

            embed = embeds.DefaultEmbed(
                f"{naam} has a new player peak!",
                f"New Peak: {peak}"
            )

            async with aiohttp.ClientSession() as session:
                for webhook_url in WEBHOOK_URLS_FORTNITE:
                    webhook = Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed)


@tasks.loop(seconds=60)
async def check_quote_send():
    if (datetime.now().hour == 8 and not bot.quote_gestuurd):
        bot.quote_gestuurd = True

        try:
            categoryies = ['happiness', 'alone', 'anger', 'change', 'courage', 'friendship', 'inspirational']
            api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(random.choice(categoryies))
            response = requests.get(api_url, headers={'X-Api-Key': os.environ.get('API_NINJAS_KEY')})
            if response.status_code == requests.codes.ok:
                data = response.json()[0]
                embed = embeds.DefaultEmbed(
                    data['quote'], 
                    f"💭 Category: {data['category']}"
                )
                embed.set_author(name=data["author"])
                
                logger.info(f"sending quote: {data['quote']}")

                # stuur embed 
                channel = bot.get_channel(int(os.environ.get("PHILOSOPHY_CHANNEL")))
                await channel.send(embed=embed)

            else:
                bot.quote_gestuurd  = False
                logger.error("Error:", response.status_code, response.text)

        except Exception as e:
            logger.error(f"Something went wrong! Try Again! {e}")
        
    elif datetime.now().hour > 8:
        bot.quote_gestuurd = False


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
        owner = int(list(os.environ.get("OWNERS").split(","))[0])
        user = await bot.fetch_user(owner)
        await user.send(content=f"{message.author.display_name} sent: {message.content}")

        for att in message.attachments:
            await user.send(content=att.url)
        


    await WordFinder.WordFinder().trigger_word(bot, message)
    
    # await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    is_poll = await db_manager.is_poll(payload.message_id)
    
    if not is_poll:
        return
    
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    
    if not user.bot:
        bot.logger.info(f"{user.display_name} voted {payload.emoji.name}")

    # remove wrong emoji reactions
    if payload.emoji.name not in emojis:
        await message.remove_reaction(payload.emoji, user)
        return 
    
    # get current reactions on poll
    reactions = await db_manager.get_poll_reactions(payload.message_id)
    reactions = reactions[0][0]

    i = emojis.index(payload.emoji.name)

    # new reaction                                      not bot initial reaction
    if str(payload.user_id) not in reactions[i] and str(payload.user_id) != os.environ.get("APPLICATION_ID"):
        # remove all previous reactions from user
        reactions = [[ subelt for subelt in elt if subelt not in [str(payload.user_id), f"'{payload.user_id}'"] ] for elt in reactions] 
        # remove 'placeholder'
        reactions = [[ subelt for subelt in elt if subelt not in ['placeholder', "'placeholder'"] ] for elt in reactions] 
        # add new user reaction
        reactions[i].append(str(payload.user_id))
        # fill subarrays with placeholders
        max_length = max([len(i) for i in reactions])
        reactions = [sub + ((max_length-len(sub)) * ['placeholder']) for sub in reactions]


    # update db with the new information
    string_reactions = repr(reactions).replace("[", "{").replace("]", "}")
    await db_manager.set_poll_reactions(payload.message_id, string_reactions)

    # delete the emoji reaction
    if str(payload.user_id) != os.environ.get("APPLICATION_ID"):
        await message.remove_reaction(payload.emoji, user)


    e = message.embeds[0]
    # remove placeholders
    reactions = [[ subelt for subelt in elt if subelt not in ['placeholder', "'placeholder'"] ] for elt in reactions] 
    
    # update message to show correct votes
    vals = [len(sub) for sub in reactions]
    total = sum(vals)
    field = '\u200b'
    for i in range(len(vals)):
        perc = 0 if total == 0 else vals[i]/total
        field += f'**{emojis[i]}: {vals[i]} votes - {perc:.0%}**\n'
    
    e.remove_field(index=1)
    e.add_field(
        name='**🏁 Results**',
        value=field,
        inline=False
    )
    
    # update thumbnail
    data = repr([str(len(sub)) for sub in reactions])
    ops = e.fields[0].value.replace("*", "").split("\n")[:-1]
    ops = repr([o[4:] for o in ops])
    url = f"https://quickchart.io/chart?c={{type:'pie',data:{{datasets:[{{data:{data}}}],labels:{ops}}}}}".replace(' ', '')
    e.set_thumbnail(
        url=url
    )

    # update the message with the edited embed
    await message.edit(embed=e)



@bot.event
async def on_member_remove(member):
    bot.logger.info(f"increased ban count of {member.id}")
    await db_manager.increment_or_add_ban_count(member.id, 1)


@bot.event
async def on_member_join(member):
    bot.logger.info(f"{member.id} joined a server!")

    description = ""
    # autonick
    nick = await db_manager.get_nickname(member.guild.id, member.id)

    if nick not in [None, -1]:
        await member.edit(nick=nick[0])
        bot.logger.info(f'Autonick set')
        description += f"Your nickname is now '{nick[0]}'.\n"

    # autoroles
    roles_to_add = await db_manager.get_autoroles(member.guild.id, member.id)
    
    # add default member role
    if str(member.guild.id) == str(os.environ.get("GUILD_ID")):
        if roles_to_add in [None, -1]:
            roles_to_add = []
            roles_to_add.append([os.environ.get("MEMBER_ROLE_ID")])
            
        else:
            roles_to_add[0].append(os.environ.get("MEMBER_ROLE_ID"))

    if roles_to_add not in [None, -1]:
        
        roles_to_add = [int(role_id) for role_id in roles_to_add[0]]

        # add roles to user
        for role_id in roles_to_add:
            try:
                new_role = discord.utils.get(member.guild.roles, id=role_id)
                await member.add_roles(new_role)
            except:
                bot.logger.warning(f"role {role_id} not found")
        
        bot.logger.info(f"Added autoroles")
        description += f"You got your roles back!"

    embed = embeds.DefaultEmbed(
        f"Welcome to {member.guild.name}!", description
    )

    try:
        embed.set_thumbnail(member.guild.icon.url)
    except:
        pass

    # send welcome to user
    await member.send(embed=embed)
    
        

@bot.event
async def on_app_command_completion(interaction, command) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed.

    :param context: The context of the command that has been executed.
    """
    full_command_name = command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if interaction.guild is not None:
        bot.logger.info(
            f"Executed {executed_command} command in {interaction.guild.name} (ID: {interaction.guild_id}) by {interaction.user} (ID: {interaction.user.id})"
        )
    else:
        bot.logger.info(
            f"Executed {executed_command} command by {interaction.user} (ID: {interaction.user.id}) in DMs"
        )

    # add stats to db
    await db_manager.increment_or_add_command_count(interaction.user.id, executed_command, 1)


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


async def on_tree_error(interaction, error):
    """
    The code in this event is executed every time a command catches an error.

    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = embeds.OperationFailedEmbed(
            f"**Please slow down** - You can use this command again in {f'{round(hours)} hours ' if round(hours) > 0 else ''}{f'{round(minutes)} minutes ' if round(minutes) > 0 else ''}{f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            emoji="⏲️"
        )

        # send out response
        if interaction.response.is_done():
            return await interaction.followup.send(embed=embed, ephemeral=True)
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    elif isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.not_blacklisted() check in your command, or you can raise the error by yourself.
        """
        embed = embeds.OperationFailedEmbed(
            "You are blacklisted from using the bot!",
        )

        if interaction.guild:
            bot.logger.warning(
                f"{interaction.user} (ID: {interaction.user.id}) tried to execute a command in the guild {interaction.guild.name} (ID: {interaction.guild_id}), but the user is blacklisted from using the bot."
            )
        else:
            bot.logger.warning(
                f"{interaction.user} (ID: {interaction.user.id}) tried to execute a command in the bot's DMs, but the user is blacklisted from using the bot."
            )

    elif isinstance(error, exceptions.UserNotOwner):
        """
        Same as above, just for the @checks.is_owner() check.
        """
        embed = embeds.OperationFailedEmbed(
            "You are not the owner of the bot!",
            emoji="🛑"
        )
        if interaction.guild:
            bot.logger.warning(
                f"{interaction.user} (ID: {interaction.user.id}) tried to execute an owner only command in the guild {interaction.guild.name} (ID: {interaction.guild_id}), but the user is not an owner of the bot."
            )
        else:
            bot.logger.warning(
                f"{interaction.user} (ID: {interaction.user.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
            )

    elif isinstance(error, discord.app_commands.MissingPermissions):
        embed = embeds.OperationFailedEmbed(
            "You are missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to execute this command!",
        )

    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        embed = embeds.OperationFailedEmbed(
            "I am missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to fully perform this command!",
        )

    elif isinstance(error, exceptions.WrongChannel):
        embed = embeds.OperationFailedEmbed(
            "Wrong channel!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            str(error).capitalize(),
        )

    elif isinstance(error, exceptions.UserNotInVC):
        embed = embeds.OperationFailedEmbed(
            f"You are not in a voice channel",
            emoji="🔇"
        ) 

    elif isinstance(error, exceptions.BotNotInVC):
        embed = embeds.OperationFailedEmbed(
            f" Bot is not in vc",
            "use /join to add bot to vc",
            emoji="🔇"
        ) 

    elif isinstance(error, exceptions.BotNotPlaying):
        embed = embeds.OperationFailedEmbed(
            f"The bot is not playing anything at the moment.",
            "Use /play to play a song or playlist",
            emoji="🔇"
        )
    
    elif isinstance(error, exceptions.TimeoutCommand):
        embed = embeds.OperationFailedEmbed(
            "You took too long!",
            emoji="⏲️"
        )
    
    elif isinstance(error, exceptions.CogLoadError):
        embed = embeds.OperationFailedEmbed(
            title="Cog error!",
        )
    
    elif isinstance(error, discord.HTTPException):
        embed = embeds.OperationFailedEmbed(
            title="Something went wrong!",
            description="most likely daily application command limits.",
        )

    else:
        embed = embeds.OperationFailedEmbed(
            title="Error!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
        )

    bot.logger.info(error) 
    
    # send out response
    if interaction.response.is_done():
        return await interaction.followup.send(embed=embed)
    await interaction.response.send_message(embed=embed)


bot.tree.on_error = on_tree_error


async def setup_hook() -> None:

    # For dynamic items, we must register the classes instead of the views.
    bot.add_dynamic_items(DynamicVotesButton)

bot.setup_hook = setup_hook


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


async def init_fortnite_player_peak():
    bot.fornite_peaks = {}

    for naam, map_info in FORTNITE_MAPS.items():
        map_info["max"] = await get_fortnite_player_peak(map_info["mapcode"])
    

async def get_fortnite_player_peak(mapcode):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(f"https://fortnite.gg/island?code={mapcode}", headers=headers)

    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        player_stats_titles = soup.find_all('div', class_='chart-stats-title')

        return int(player_stats_titles[2].text)

    else:
        return 0



init_db()
asyncio.run(load_cogs())
bot.run(os.environ.get("TOKEN"))
