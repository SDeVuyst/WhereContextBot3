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
        #await self.check_gf(bot, message)

 
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
        if message.author.id == int(os.environ.get("YACHJA")):
            return
        
        content = message.content.replace("\n", " ").lower()
        triggers = ["one piece", "peak", "luffy"]

        # check for a trigger in the message
        if any(trigger in content for trigger in triggers):

            # send dm to yachja 
            yachja = await bot.fetch_user(int(os.environ.get("YACHJA")))
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
        

    async def check_gf(self, bot, message):
        content = message.content.replace("\n", " ").lower()
        triggers = ["danae", "danea", "danaë"]
        responses = ["<@222415043550117888> pedo ass mf", '<@222415043550117888> pre-ordered :sob:', "<@222415043550117888> bro going to jail :sob::sob:", "<@222415043550117888> early investor :skull:", "https://i.imgur.com/Qtjijog.gif", "https://imgur.com/a/vybyj9s", "https://cdn.discordapp.com/attachments/1114464141508345906/1159560172558098452/61keJhuI4HS._AC_UF10001000_QL80_.jpg?ex=65317790&is=651f0290&hm=be37960b453805393dc9a84464a2db1b261c62e2e3e309998ed4633778c84ede&", 'How do you make a little girl cry twice in a row? - You wipe the blood off your cock on her teddybear before you leave. -<@222415043550117888>', 'What do you do after you lick the smoothest pussy in the world? - Put the diaper back on. -<@222415043550117888>', "<@222415043550117888> is niet zo'n slecht persoon, hij rijdt tenminste traag in de schoolzone", "geen wonder da <@222415043550117888> zo dik is, hij wilt zn buns vers uit de oven", "https://tenor.com/view/are-you-ready-kids-sponge-bob-meme-sponge-bob-squarepants-pirate-gif-14124417", "https://media.discordapp.net/attachments/727476894106386504/1161646871354298520/image.png?ex=65390ef4&is=652699f4&hm=34f3cf7b89289384f86e391f5e7de24f4689d68ebc5207815e90dd069b3750e7&=&width=1735&height=993"]

        # check for a trigger in the message
        if any(trigger in content for trigger in triggers):
            await message.reply(random.choice(responses), silent=True)
            # update db
            await db_manager.increment_or_add_command_count(message.author.id, 'danae', 1)
            bot.logger.info(f"danae trigger by {message.author.display_name}: {message.content}")