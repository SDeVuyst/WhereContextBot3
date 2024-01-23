""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

from discord import app_commands


class UserBlacklisted(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is blacklisted.
    """

    def __init__(self, message="User is blacklisted!"):
        self.message = message
        super().__init__(self.message)


class UserNotOwner(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not an owner of the bot.
    """

    def __init__(self, message="User is not an owner of the bot!"):
        self.message = message
        super().__init__(self.message)


class WrongChannel(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is in the wrong channel.
    """

    def __init__(self, message="Wrong channel!"):
        self.message = message
        super().__init__(self.message)


class UserNotInVC(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not in a voice channel
    """

    def __init__(self, message="User is not in a voice channel."):
        self.message = message
        super().__init__(self.message)


class BotNotInVC(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but the bot is not in a voice channel.
    """

    def __init__(self, message="Bot is not in a voice channel."):
        self.message = message
        super().__init__(self.message)


class BotNotPlaying(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but the bot is not playing audio.
    """

    def __init__(self, message="Bot is not playing anything."):
        self.message = message
        super().__init__(self.message)


class TimeoutCommand(app_commands.CheckFailure):
    """
    Thrown when a user has exceeded a time limit.
    """

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class CogLoadError(app_commands.CheckFailure):
    """
    Thrown when a cog doesnt load correctly.
    """

    def __init__(self, cog, status):
        if status == 0:
            errortype = 'load'
        elif status == 1:
            errortype = 'unload'
        else:
            errortype = 'reload'

        self.message = f"Could not {errortype} cog." if not cog else f"Could not {errortype} the ```{cog}``` cog."
        super().__init__(self.message)