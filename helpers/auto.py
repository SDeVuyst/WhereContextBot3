import discord

async def autoroles(bot, member):
    # add member role
    member_role = discord.utils.get(member.guild.roles, id=753959093185675345)
    await member.add_roles(member_role)

    roles = {
        "perms": 756224050237538325,
        "techgod": 1079432980038172805,
        "gent": 1024341053786038332,
        "fakonepiece": 970418792012325008,
        "fortnut": 946064405597138994,
        "spooderman": 918990342840275035,
        "genshin": 817107290708639774,
        "waifubot": 778688939623710770,
        "wcb3": 1119600252228489296,
        "retarded": 738782795673108572,
        "minecraft": 739212609248690248,
        "notcultured": 805130046414127126,
        "cultured": 740301828071358738,
        "homeless": 801146953470967809,
        "cringe": 836973694630887455,
        "degeneratevandejaar": 864947578554023986,
        "owner": 799385460677804043,
        "titanfood": 787665548506955776,
        "sugardaddy": 827108224485294100,
        "perms": 756224050237538325,
        "yachja": 1119328394568548402,
        "knie": 1129051258657968208,
        "cummaster": 851467556040474624,
        "meng": 777956016033103872,
        "mongwongs": 1146529770297888961
    }

    members = {
        # solos
        462932133170774036: ["mongwongs", "meng", "cummaster", "owner", "notcultured", "perms", "techgod", "gent", "spooderman", "wcb3", "minecraft"],
        # broodman
        733845345225670686: ["mongwongs", "yachja", "cultured", "perms", "gent", "spooderman", "waifubot", "minecraft"],
        # arion
        334371900170043402: ["mongwongs", "meng", "cultured", "perms", "techgod", "fortnut", "spooderman", "minecraft"],
        # pingy
        464400950702899211: ["mongwongs", "knie", "titanfood", "cringe", "cultured", "perms", "gent", "fortnut", "spooderman", "genshin", "waifubot", "minecraft"],
        # ba
        222415043550117888: ["mongwongs", "meng", "cummaster", "titanfood", "cultured", "perms", "gent", "fortnut", "spooderman", "genshin", "waifubot", "minecraft"],
        # nootje
        273503117348306944: ["mongwongs", "sugardaddy", "homeless", "notcultured", "perms", "gent", "minecraft"],
        # zeb
        756527409876041859: ["titanfood", "degeneratevandejaar", "cringe", "notcultured", "fakonepiece", "spooderman", "genshin", "waifubot", "retarded", "minecraft"],
        # lendar
        527916521754722315: ["mongwongs", "meng", "cummaster", "cultured", "perms", "gent", "waifubot", "minecraft"],
        # xander
        548544519793016861: ["titanfood", "cultured", "gent", "waifubot", "minecraft"],
        # gible
        559715606014984195: ["mongwongs", "notcultured", "gent", "minecraft"],
        # meng
        512256261459542019: ["mongwongs", "meng", "cummaster", "cultured", "perms", "gent", "genshin", "minecraft"],
        # wouter
        453136562885099531: ["cultured"],
        # zyfo
        494508091283603462: ["mongwongs", "notcultured", "perms", "techgod", "minecraft"],

    }
    

    if member.id in members:

        # voeg autoroles toe
        for role in members.get(member.id):
            try:
                new_role = discord.utils.get(member.guild.roles, id=roles.get(role))
                await member.add_roles(new_role)
            except:
                bot.logger.warning(f"role {role} not found")

        
        bot.logger.info(f"Added autoroles")
        await member.send('Added your roles back!')



async def autonick(bot, member):
    nicks = {
        # yachja
        # 733845345225670686: "",
        # gible      
        559715606014984195: "smikkelkontje",     
        # arno        
        # 273503117348306944: "",
        # pingy                 
        # 464400950702899211: "",
        # solos             
        462932133170774036: "kanye east",
        # ba
        222415043550117888: "ba"

    }

    if member.id in nicks:
        await member.edit(nick=nicks.get(member.id))
        await member.send(f'Set your nickname to "{nicks.get(member.id)}"')

