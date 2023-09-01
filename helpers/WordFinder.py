from . import db_manager
import re
import os
from discord import Embed
import random

class WordFinder:
    def __init__(self) -> None:
        pass
        

    async def trigger_word(self, bot, message):
        await self.findNWord(bot, message)
        await self.find_yachja_word(bot, message)
        await self.check_gif(bot, message)

 
    async def findNWord(self, bot, message):
        content = message.content.replace("\n", " ").lower()

        # words that get detected as nwords but are not
        ban_list = ['vinager', 'vineger', 'vinegar', 'monika', 'https', 'negeer', 'enige', 'zonnig', 'nieke', 'innige']
        if any(ban in content for ban in ban_list):
            return
        
        # find nwords
        pattern = r'(^|\s|\w)?[nNɴ🇳]+[\*\|\_]*[ie1ɪi🇮]+[\*\|\_]*[gɢg🇬]+[\*\|\_]*[l]*[\*\|\_]*[eᴇea3🇦🇦rqrʀ]+[\*\|\_]*[s]*'
        count = len(re.findall(pattern, content, flags=re.IGNORECASE))
        if count > 0:
            await db_manager.increment_or_add_nword(message.author.id, count)
        bot.logger.info(f"{message.author.display_name} said nword {count} times: {message.content}")
    


    async def find_yachja_word(self, bot, message):
    
        # message niet van yachja zelf
        if message.author.id == int(os.environ.get("yachja")):
            return
        
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

            bot.logger.info(f"yachja trigger: {message.content}")

            await yachja.send(embed=embed)


    async def check_gif(self, bot, message):

        # author can send gifs
        if message.author.name not in [i[0] for i in bot.gif_prohibited]:
            return
        
        responses = [
            f"<@{message.author.id}> shatap lil bro", 
            f"<@{message.author.id}> you are NOT him",
            f"<@{message.author.id}> blud thinks he's funny",
            f"<@{message.author.id}> imma touch you lil nigga",
            f"<@{message.author.id}> it's on sight now",
        ]

        if len(message.attachements) > 0:
            for attachement in message.attachements:
                if ".gif" in attachement.filename.lower():

                    # gif found
                    await message.channel.send(random.choice(responses))
                    await message.delete()
