from . import db_manager
import re

async def findNWord(bot, message):
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
    