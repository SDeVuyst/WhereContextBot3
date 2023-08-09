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


class MissingNwords(app_commands.CheckFailure):
    """
    Thrown when a user is attempting something, but has too little nwords.
    """

    def __init__(self, usercount: int, required:int):
        self.usercount = usercount
        self.required = required
        self.message = f"You need {required} N-words to use this command, but you only have {usercount}."
        super().__init__(self.message)