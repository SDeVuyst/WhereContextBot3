from . import db_manager
import embeds
import os
import random

class WordFinder:
    def __init__(self) -> None:
        pass
        

    async def trigger_word(self, bot, message):
        await self.find_yachja_word(bot, message)
        await self.check_gif(bot, message)
        #await self.check_gf(bot, message)


    async def find_yachja_word(self, bot, message):
    
        # message niet van yachja zelf
        if message.author.id == int(os.environ.get("YACHJA")):
            return
        
        content = message.content.replace("\n", " ").lower()
        triggers = ["one piece", "peak", "luffy"]

        # check for a trigger in the message
        if any(trigger in content for trigger in triggers):

            # send dm to yachja 
            yachja = await bot.fetch_user(int(os.environ.get("YACHJA")))

            bot.logger.info(f"yachja trigger: {message.content}")

            await yachja.send(embed=embeds.DefaultEmbed(
                "One piece talk! 🗣️", f"[Go to message]({message.jump_url})"
            ))


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

        # gif via link
        if "gif" in message.content:
            # gif found
            await message.channel.send(random.choice(responses))
            await message.delete()
            return
        
        # gif via attachments
        if len(message.attachments) > 0:
            await message.channel.send(random.choice(responses))
            await message.delete()
            return
        