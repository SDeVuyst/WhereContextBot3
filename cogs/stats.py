""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
from discord import app_commands
from discord.components import SelectOption
from discord.ext import commands
from discord.ext.commands import Context
from discord.interactions import Interaction
from discord.ui import Select, View

from helpers import checks, db_manager



class Stats(commands.Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot
        self.timeout_embed = discord.Embed(
            title="You took too long!",
            color=self.bot.errorColor
        )
        
    async def get_stat_individual_embed(self, userid, command):
        """Get an embed for individual stats

        Args:
            userid (str): Id of user 
            command (str): Which command

        Returns:
            Embed
        """
        count = await db_manager.get_command_count(userid, command)
        # Geen berichten
        if len(count) == 0 or int(count[0][0]) == 0:
            embed = discord.Embed(
                description=f"**<@{userid}> didn't use {command} yet.**",
                color=self.bot.defaultColor
            )
            return embed
        
        # error
        elif count[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=count[1],
                color=self.bot.errorColor
            )
            return embed
        
        if command == "messages_played":
            desc = f"**<@{userid}> played```{count[0][0]}``` messages.**"
        elif command == "messages_deleted":
            desc = f"**<@{userid}> deleted```{count[0][0]}``` messages.**"
        elif command == "ncountCHECK":
            desc = f"<@{userid}> said the n-word ```{count[0][0]}``` times.**"
        else:
            desc = f"**<@{userid}> used {command} ```{count[0][0]}``` times.**"

        embed = discord.Embed(
            title="📊 Individual Statistic",
            description=desc,
            color=self.bot.defaultColor
        )

        return embed



    @app_commands.command(
        name="individuele_stats",
        description="How many times did a user use a command",
        extras={'cog': 'stats'}
    )
    @app_commands.describe(user="Welke persoon")
    @checks.not_blacklisted()
    @commands.cooldown(rate=1, per=10)
    async def stats_individual(self,interaction, user: discord.User) -> None:
        """Shows the individual stats for a user for a given command

        Args:
            interaction (Interaction): Users interaction
            user (discord.User): Which user
        """
        view = CommandView(self.bot)
        await interaction.response.send_message(view=view)
        await view.wait()
        if view.chosen_command is None:
            embed = self.timeout_embed 
        else:
            embed = await self.get_stat_individual_embed(user.id, view.chosen_command)
        
        await interaction.message.edit(embed=embed)
        


    @app_commands.command(name="changecommandcount", description="Change the command count of a user (admin only)", extras={'cog': 'stats'})
    @app_commands.describe(user="Which users count")
    @checks.is_owner()
    async def change_command_count(self,interaction, user: discord.User, amount: int):
        """Changes the count of a command for a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user
            amount (int): What to set the count to
        """
        view = CommandView(self.bot)
        await interaction.response.send_message(view=view)
        await view.wait()

        if view.chosen_command is None:
            embed = self.timeout_embed 
        else:
            # krijg count uit db
            succes = await db_manager.set_command_count(view.chosen_command, user.id, amount)

            # verstuur embed
            desc = f"{view.chosen_command} count of <@{user.id}> is now {amount}" if succes else "Something went wrong"
            embed = discord.Embed(
                title="Succes!" if succes else "Oops!",
                description=desc,
                color=self.bot.succesColor if succes else self.bot.defaultColor
            )
        
        await interaction.followup.send(embed=embed)



    async def get_leaderboard_embed(self, command):
        """Get embed for a leaderboard 

        Args:
            command (str): Which command

        Returns:
            Embed
        """
        if command == "ncountCHECK":
            leaderb = await db_manager.get_nword_leaderboard()
        elif command == "bancount":
            leaderb = await db_manager.get_ban_leaderboard()
        else:
            # krijg count bericht uit db
            leaderb = await db_manager.get_leaderboard(command)

        # Geen berichten
        if len(leaderb) == 0:
            embed = discord.Embed(
                description=f"**This command has not been used yet.**",
                color=self.bot.succesColor
            )
            return embed
        
        # error
        elif leaderb[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=leaderb[1],
                color=self.bot.errorColor
            )
            return embed
        
        desc = ""
        for i, stat in enumerate(leaderb):
            user_id, count = tuple(stat)
            desc += f"{i+1}: **<@{int(user_id)}>  ⇨ {count}**\n\n"

        command = "N-words said" if command == "ncountCHECK" else command

        embed = discord.Embed(
            title=f"🏆 Leaderboard for {command}",
            description=desc,
            color=self.bot.defaultColor
        )

        return embed



    @app_commands.command(name="leaderboard", description="Leaderboard of a command", extras={'cog': 'stats'})
    @checks.not_blacklisted()
    @commands.cooldown(rate=1, per=10)
    async def leaderboard(self,interaction):
        """Shows the leaderboard for a command

        Args:
            interaction (Interaction): Users interaction
        """
        view = CommandView(self.bot)
        await interaction.response.send_message(view=view)
        await view.wait()
        if view.chosen_command is None:
            embed = self.timeout_embed 
        else:
            embed = await self.get_leaderboard_embed(view.chosen_command)

        await interaction.followup.send(embed=embed)
        


    @app_commands.command(name="bancount", description="How many times has a user been banned?", extras={'cog': 'stats'})
    @app_commands.describe(user="Which users ban count")
    @checks.not_blacklisted()
    async def bancount(self,interaction, user: discord.User):
        """How many times a user has been banned

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which users ban count
        """
        
        # krijg count uit db
        count = await db_manager.get_ban_count(user.id)

        # Geen berichten
        if len(count) == 0 or int(count[0][0]) == 0:
            embed = discord.Embed(
                description=f"❌ **<@{user.id}> has not been banned yet**",
                color=self.bot.defaultColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # error
        elif count[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=count[1],
                color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        

        embed = discord.Embed(
            description=f"🔨 **<@{user.id}> has been banned ```{count[0][0]}``` times.**",
            color=self.bot.defaultColor
        )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="changebancount", description="Change user ban count (owner only)", extras={'cog': 'stats'})
    @checks.is_owner()   
    async def change_ban_count(self,interaction, user: discord.User, amount: int):
        """Changes the ban count of a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user
            amount (int): Set the count to 
        """
        # krijg count uit db
        succes = await db_manager.set_ban_count(user.id, amount)


        # verstuur embed
        desc = f"ban count of <@{user.id}> is now {amount}" if succes else "Something went wrong"
        embed = discord.Embed(
            title="Succes!" if succes else "Oops!",
            description=desc,
            color=self.bot.succesColor if succes else self.bot.defaultColor
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="ncount", description="AYO??", extras={'cog': 'stats'})
    @app_commands.describe(user="Which users' n-word count")
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @commands.cooldown(rate=1, per=10)
    async def nCount(self,interaction, user: discord.User):
        """How many times a user has said the nword

        Args:
            interaction (Interaction): Users interaction
            user (discord.User): Which user
        """

        # krijg count bericht uit db
        count = await db_manager.get_nword_count(user.id)

        # Geen berichten
        if len(count) == 0 or int(count[0][0]) == 0:
            embed = discord.Embed(
                description=f"😌 **NWord Count of <@{user.id}>:** ```0```",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # error
        elif count[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=count[1],
                color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            description=f"📸 **NWord Count of <@{user.id}>:** ```{count[0][0]}```",
            color=self.bot.defaultColor
        )


        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name="changencount", description="Change the count of a user (admin only)", extras={'cog': 'stats'})
    @app_commands.describe(user="Which users' n-word count")
    @app_commands.describe(amount="Amount to set the count to")
    @checks.is_owner()
    async def changeNCount(self,interaction, user: discord.User, amount: int):
        """Change the ncount of a user

        Args:
            interaction (Interaction): Users interaction
            user (discord.User): Which user
            amount (int): Set to how much
        """

        # krijg count uit db
        succes = await db_manager.set_nword_count(user.id, amount)

        # verstuur embed
        desc = f"NWord Count of <@{user.id}> is now {amount}" if succes else "Something went wrong"
        embed = discord.Embed(
            title="Succes!" if succes else "Oops!",
            description=desc,
            color=self.bot.succesColor if succes else self.bot.defaultColor
        )
        await interaction.response.send_message(embed=embed)



class CommandView(View):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

    chosen_command = None

    @discord.ui.select(
        placeholder="Kies een onderverdeling",
        options = [
            SelectOption(label="Audio", emoji="🎙️", value="audio"),
            SelectOption(label="General", emoji="🤖", value="general"),
            SelectOption(label="Statistics", emoji="📊", value="stats"),
            SelectOption(label="Out Of Context", emoji="📸", value="outofcontext"),
            SelectOption(label="Reacties", emoji="💭", value="reacties"),
            SelectOption(label="Owner", emoji="👨‍🔧", value="owner")
        ]     
    )
    async def select_cog(self, interaction: Interaction, select_item : Select):
        """Selection of first cog

        Args:
            interaction (Interaction): Users interaction
            select_item (Select): Selected item
        """
        self.children[0].disabled = True
        self.children[0].placeholder = select_item.values[0]
        command_select = CommandSelect(self.bot, select_item.values[0])
        self.add_item(command_select)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def respond_to_answer2(self, interaction : Interaction, choices):
        """What to do after second choice aka user has chosen a command

        Args:
            interaction (Interaction): Users interaction
            choices (list): What has the user chosen
        """
        self.chosen_command = choices[0]
        self.children[1].disabled= True
        self.children[1].placeholder = choices[0]
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


class CommandSelect(Select):
    def __init__(self, bot, selected_cog):
        commands = []
        for y in bot.tree.walk_commands():
            if y.extras.get('cog') == selected_cog:
                commands.append((y.name, y.name))

        # stats die zelf geen command zijn
        if selected_cog == "outofcontext":
            commands.append(("Messages Played", "messages_played"))
            commands.append(("Messages Deleted", "messages_deleted"))
        
        elif selected_cog == "stats":
            commands.insert(0, ("N-Words said", "ncountCHECK"))


        super().__init__(
            placeholder="Kies een command", 
            options=[SelectOption(label=label, value=value) for label, value in commands]
        )

    async def callback(self, interaction:Interaction):
        await self.view.respond_to_answer2(interaction, self.values)


async def setup(bot):
    await bot.add_cog(Stats(bot))
