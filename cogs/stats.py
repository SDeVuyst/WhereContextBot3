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
from discord.interactions import Interaction
from discord.ui import Select, View

from helpers import ArtBuilder, checks, db_manager
from exceptions import TimeoutCommand


class Stats(commands.Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot
        
    
    @app_commands.command(
            name="leaderboard",
            description="Leaderboard of a command", 
            extras={'cog': 'stats'}
    )
    @checks.not_blacklisted()
    @checks.is_owner() # TODO remove
    @app_commands.checks.cooldown(rate=1, per=10)
    async def leaderboard(self,interaction):
        """Shows the leaderboard for a command

        Args:
            interaction (Interaction): Users interaction
        """
        view = CommandView(self.bot)
        await interaction.response.send_message(view=view)

        secondMessage = await interaction.channel.send('** **')
        
        await view.wait()

        

        if view.chosen_command is None:
            raise TimeoutCommand('Timeout in /leaderboard')

        elif view.chosen_command == "bancount":
            leaderb = await db_manager.get_ban_leaderboard()

        else:
            # krijg count bericht uit db
            leaderb = await db_manager.get_leaderboard(view.chosen_command)
        
        # Geen berichten
        if len(leaderb) == 0:
            embed = discord.Embed(
                description=f"❌ **This command has not been used yet.**",
                color=self.bot.default_color
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        
        # error
        elif leaderb[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=leaderb[1],
                color=self.bot.error_color
            )
            return await interaction.edit_original_response(embed=embed, view=None)
         
        if view.chosen_command == "danae":
            command = "danae trigger"
        elif view.chosen_command == "keleo":
            command = "keleo trigger"
        else:
            command = f'/{view.chosen_command}'
        
        builder = ArtBuilder.LeaderboardBuilder(self.bot)

        top = await builder.get_top_leaderboard(leaderb, command)
        await interaction.edit_original_response(attachments=[top], view=None, embed=None)

        bottom = await builder.get_bottom_leaderboard(leaderb)
        await secondMessage.add_files(bottom)



    @app_commands.command(
        name="statistic",
        description="How many times did a user use a feature",
        extras={'cog': 'stats'}
    )
    @app_commands.describe(user="Welke persoon")
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=1, per=10)
    async def statistic(self,interaction, user: discord.User = None) -> None:
        """Shows the individual stats for a user for a given command

        Args:
            interaction (Interaction): Users interaction
            user (discord.User): Which user
        """

        # geen gebruiker meegegeven, gaat over zichzelf
        if user is None:
            user = interaction.user

        # send view to get chosen command
        view = CommandView(self.bot)
        await interaction.response.send_message(view=view)
        await view.wait()

        # timeout
        if view.chosen_command is None:
            raise TimeoutCommand("Timeout in /statistic")

        #  generate response
        embed = await self.get_stat_individual_embed(user.id, view.chosen_command)
        
        await interaction.edit_original_response(embed=embed, view=None)



    async def get_stat_individual_embed(self, userid, command):
        """Get an embed for individual stats

        Args:
            userid (str): Id of user 
            command (str): Which command

        Returns:
            Embed
        """
        if command == "bancount":
            count = await db_manager.get_ban_count(userid)
        else:
            # krijg count bericht uit db
            count = await db_manager.get_command_count(userid, command)

        
        # Geen berichten
        if len(count) == 0 or int(count[0][0]) == 0:
            if command == "bancount":
                desc = f"🔨 **<@{userid}> has not been banned yet.**"
            elif command == "danae":
                desc = f"✌️ **<@{userid}> has not triggered the danae feature yet.**"
            elif command == "keleo":
                desc = f"✌️ **<@{userid}> has not triggered the keleo feature yet.**"
            else:
                desc = f"❌ **<@{userid}> didn't use /{command} yet.**"

            embed = discord.Embed(
                description=desc,
                color=self.bot.default_color
            )
            return embed
        
        # error
        elif count[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=count[1],
                color=self.bot.error_color
            )
            return embed
        
        if command == "messages_played":
            desc = f"**<@{userid}> played```{count[0][0]}``` messages.**"
        elif command == "messages_deleted":
            desc = f"**<@{userid}> deleted```{count[0][0]}``` messages.**"
        elif command == "danae":
            desc = f"**<@{userid}> triggered 'danae' ```{count[0][0]}``` times.**"
        elif command == "keleo":
            desc = f"**<@{userid}> triggered 'keleo' ```{count[0][0]}``` times.**"
        elif command == "bancount":
            desc = f"🔨 **<@{userid}> has been banned ```{count[0][0]}``` times.**"
        else:
            desc = f"**<@{userid}> used {command} ```{count[0][0]}``` times.**"

        embed = discord.Embed(
            title="📊 Individual Statistic",
            description=desc,
            color=self.bot.default_color
        )

        return embed



class CommandView(View):
    def __init__(self, bot) -> None:
        super().__init__(timeout=60)
        self.bot = bot
        self.feature_selector = None

    chosen_command = None

    @discord.ui.select(
        placeholder="Choose a subdivision",
        options = [
            SelectOption(label="Audio", emoji="🎙️", value="audio"),
            SelectOption(label="General", emoji="🤖", value="general"),
            SelectOption(label="Statistics", emoji="📊", value="stats"),
            SelectOption(label="Out Of Context", emoji="📸", value="outofcontext"),
            SelectOption(label="Admin", emoji="👨‍🔧", value="admin")
        ]     
    )
    async def select_cog(self, interaction: Interaction, select_item : Select):
        """Selection of first cog

        Args:
            interaction (Interaction): Users interaction
            select_item (Select): Selected item
        """
        formatted = {
            "audio": "🎙️ Audio",
            "general": "🤖 General",
            "stats": "📊 Statistics",
            "outofcontext": "📸 Out Of Context",
            "admin": "👨‍🔧 Admin"
        }
        # self.children[0].disabled = True
        self.children[0].placeholder = formatted[select_item.values[0]]
        command_select = CommandSelect(self.bot, select_item.values[0])

        # remove previous selected feature selector if necessary
        if self.feature_selector is not None:
            self.remove_item(self.feature_selector)

        # add selector to view
        self.add_item(command_select)
        self.feature_selector = command_select

        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def respond_to_answer2(self, interaction : Interaction, choices):
        """What to do after second choice aka user has chosen a command

        Args:
            interaction (Interaction): Users interaction
            choices (list): What has the user chosen
        """
        self.chosen_command = choices[0]
        embed = discord.Embed(
            title="⏳ Loading...",
            description="This can take a while.",
            color=self.bot.default_color
        )
        await interaction.message.edit(view=None, embed=embed)

        await interaction.response.defer()
        self.stop()


class CommandSelect(Select):
    def __init__(self, bot, selected_cog):
        commands = []
        for y in bot.tree.walk_commands():
            if y.extras.get('cog') == selected_cog:
                name = f"/{y.name}" if not y.extras.get('prefix') else f"/{y.extras.get('prefix')} {y.name}"
                commands.append((name, y.name))

        # stats die zelf geen command zijn
        if selected_cog == "outofcontext":
            commands.append(("Messages Played In Game", "messages_played"))
            commands.append(("Messages Deleted In Game", "messages_deleted"))
            commands.append(("Messages Added", "Add"))
            commands.append(("Messages Deleted", "Remove"))
        
        elif selected_cog == "stats":
            commands.insert(0, ("Bans", "bancount"))
            commands.insert(0, ("Danae trigger", "danae"))
            commands.insert(0, ("Keleo trigger", "keleo"))
        

        super().__init__(
            placeholder="Pick a feature", 
            options=[SelectOption(label=label, value=value) for label, value in commands]
        )

    async def callback(self, interaction:Interaction):
        await self.view.respond_to_answer2(interaction, self.values)


async def setup(bot):
    await bot.add_cog(Stats(bot))
