import discord

async def autoroles(bot, member):
    # add member role
    member_role = discord.utils.get(member.guild.roles, id=753959093185675345)
    await member.add_roles(member_role)

    roles = {
        # yachja                   minecraft           cultured            perms               yachja
        733845345225670686: [739212609248690248, 740301828071358738, 1119328394568548402],
        # gible                    gent                minecraft
        559715606014984195: [1024341053786038332, 739212609248690248],
        # arno                     perms               homeless          sugardaddy          gent                minecraft         
        273503117348306944: [756224050237538325, 801146953470967809, 827108224485294100, 1024341053786038332, 739212609248690248],
        # pingy                    knie                 fortnut           spooderman          genshin             waifu bot             gent                minecraft           cultured            cringe             titanfood           perms
        464400950702899211: [1129051258657968208, 946064405597138994, 918990342840275035, 817107290708639774, 778688939623710770, 1024341053786038332, 739212609248690248,740301828071358738, 836973694630887455, 787665548506955776, 756224050237538325],
        # solos                indian tech god           gent              spooderman           wcb3                minecraft       not cultured         owner               perms               meng              cummaster
        462932133170774036: [1079432980038172805, 1024341053786038332, 918990342840275035, 1119600252228489296, 739212609248690248, 805130046414127126, 799385460677804043, 756224050237538325, 777956016033103872, 851467556040474624]
    }

    

    if member.id in roles:

        # voeg autoroles toe
        roles_to_add = roles.get(member.id)
        for role_id in roles_to_add:
            try:
                new_role = discord.utils.get(member.guild.roles, id=role_id)
                
                await member.add_roles(new_role)
            except:
                bot.logger.warning(f"role {role_id} not found")

        
    bot.logger.info(f"Added autoroles")
    await member.send('Added your roles back!')


async def autonick(bot, member):
    nicks = {
        # yachja
        733845345225670686: "the flesh 🥩",
        # gible      
        559715606014984195: "smikkelkontje",     
        # arno        
        # 273503117348306944: "",
        # pingy                 
        # 464400950702899211: "",
        # # solos             
        462932133170774036: "kanye east",
    }

    if member.id in nicks:
        await member.edit(nick=nicks.get(member.id))
        await member.send(f'Set your nickname to "{nicks.get(member.id)}"')

