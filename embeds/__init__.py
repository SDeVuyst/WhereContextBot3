import discord
from datetime import datetime



DEFAULT_COLOR = 0xF4900D
ERROR_COLOR = 0xE02B2B
SUCCES_COLOR = 0x39AC39



class OperationFailedEmbed(discord.Embed):
    def __init__(self, title, description=None, emoji="❌"):
        super().__init__(
            title=f"{emoji} {title}", 
            description = description,
            color=ERROR_COLOR,
            timestamp = datetime.utcnow()
        )



class OperationSucceededEmbed(discord.Embed):
    def __init__(self, title, description=None, emoji="✅"):
        super().__init__(
            title=f"{emoji} {title}",
            description=description,
            color=SUCCES_COLOR,
            timestamp=datetime.utcnow(),
        )



class RedBorderEmbed(discord.Embed):
    def __init__(self, title, description=None):
        super().__init__(
            title=f"{title}",
            description = description,
            color=ERROR_COLOR,
            timestamp = datetime.utcnow(),  
        )



class DefaultEmbed(discord.Embed):
    def __init__(self, title, description=None):
        super().__init__(
            title=f"{title}",
            description = description,
            color=DEFAULT_COLOR,
            timestamp = datetime.utcnow(),
        )
        