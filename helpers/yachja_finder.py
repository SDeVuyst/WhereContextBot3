import os
from discord import Embed

async def find_word(bot, message):
    
    content = message.content.replace("\n", " ").lower()
    triggers = ["one piece", "one peak", "peak", "luffy"]

    # check for a trigger in the message
    if any(trigger in content for trigger in triggers):

        # send dm to yachja 
        yachja = await bot.fetch_user(int(os.environ.get("yachja")))
        embed = Embed(
            title="One piece talk! 🗣️",
            description=f"[Go to message]({message.jump_url})",
            color=bot.defaultColor,
        )

        await yachja.send(embed=embed)
