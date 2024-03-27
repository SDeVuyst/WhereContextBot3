import discord
from datetime import datetime

URLS = {
    "339820557086228490": "https://i.imgur.com/sVd3QyY.png"  
}

DEFAULT_COLOR = 0xF4900D
ERROR_COLOR = 0xE02B2B
SUCCES_COLOR = 0x39AC39



class OperationFailedEmbed(discord.Embed):
    def __init__(self, title, description=None, emoji="❌", user=None):
        super().__init__(
            title=f"{emoji} {title}", 
            description = description,
            color=ERROR_COLOR,
            timestamp = datetime.now()
        )

        if user is not None:
            self.set_thumbnail(
                url=URLS.get(str(user.id), str(user.avatar.url))
            )



class OperationSucceededEmbed(discord.Embed):
    def __init__(self, title, description=None, emoji="✅", user=None):
        super().__init__(
            title=f"{emoji} {title}",
            description=description,
            color=SUCCES_COLOR,
            timestamp=datetime.now(),
        )

        if user is not None:
            self.set_thumbnail(
                url=URLS.get(str(user.id), str(user.avatar.url))
            )



class RedBorderEmbed(discord.Embed):
    def __init__(self, title, description=None, user=None):
        super().__init__(
            title=f"{title}",
            description = description,
            color=ERROR_COLOR,
            timestamp = datetime.now(),  
        )

        if user is not None:
            self.set_thumbnail(
                url=URLS.get(str(user.id), str(user.avatar.url))
            )



class DefaultEmbed(discord.Embed):

    def __init__(self, title, description=None, user=None):
        super().__init__(
            title=f"{title}",
            description = description,
            color=DEFAULT_COLOR,
            timestamp = datetime.now(),
        )

        if user is not None:
            self.set_thumbnail(
                url=URLS.get(str(user.id), str(user.avatar.url))
            )