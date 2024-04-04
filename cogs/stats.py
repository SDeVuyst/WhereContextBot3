""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import discord

import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.components import SelectOption
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Select, View
import embeds
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
    @checks.not_in_dm()
    @app_commands.checks.cooldown(rate=1, per=10, key=lambda i: (i.guild_id, i.user.id))
    async def leaderboard(self,interaction):
        """Shows the leaderboard for a command

        Args:
            interaction (Interaction): Users interaction
        """
        await interaction.response.defer()

        view = CommandView(self.bot, is_leaderboard=True)
        first_message = await interaction.followup.send(view=view)

        second_message = await interaction.channel.send('** **')
        
        await view.wait()        

        if view.chosen_command is None:
            raise TimeoutCommand('Timeout in /leaderboard')

        elif view.chosen_command == "bancount":
            leaderb = await db_manager.get_ban_leaderboard()

        elif view.chosen_command == "ban_gamble_ratio":
            leaderb = await db_manager.get_ratio_leaderboard()

        elif view.chosen_command == "current_win_streak":
            leaderb = await db_manager.get_current_win_streak_leaderboard()

        elif view.chosen_command == "current_loss_streak":
            leaderb = await db_manager.get_current_loss_streak_leaderboard()

        elif view.chosen_command == "highest_win_streak":
            leaderb = await db_manager.get_highest_win_streak_leaderboard()

        elif view.chosen_command == "highest_loss_streak":
            leaderb = await db_manager.get_highest_loss_streak_leaderboard()

        elif view.chosen_command == "ban_total_wins":
            leaderb = await db_manager.get_ban_total_wins_leaderboard()

        elif view.chosen_command == "ban_total_losses":
            leaderb = await db_manager.get_ban_total_losses_leaderboard()

        else:
            # krijg count bericht uit db
            leaderb = await db_manager.get_leaderboard(view.chosen_command)
        
        # Geen berichten
        if len(leaderb) == 0:
            return await interaction.edit_original_response(embed=embeds.OperationFailedEmbed(
                "**This command has not been used yet.**"
            ), view=None)
        
        # error
        elif leaderb[0] == -1:
            return await interaction.edit_original_response(embed=embeds.OperationFailedEmbed(
                "Something went wrong...", leaderb[1]
            ), view=None)

        elif view.chosen_command == "ban_gamble_ratio":
            command = "Ban Gamble - Ratio"

        elif view.chosen_command == "current_win_streak":
            command = "Ban Gamble - Current Win Streak"

        elif view.chosen_command == "current_loss_streak":
            command = "Ban Gamble - Current Loss Streak"

        elif view.chosen_command == "highest_win_streak":
            command = "Ban Gamble - Highest Win Streak"

        elif view.chosen_command == "highest_loss_streak":
            command = "Ban Gamble - Highest Loss Streak"

        elif view.chosen_command == "ban_total_wins":
            command = "Ban Gamble - Total Wins"

        elif view.chosen_command == "ban_total_losses":
            command = "Ban Gamble - Total Losses"

        elif view.chosen_command == "bancount":
            command = "Bans"

        else:
            command = f'/{view.chosen_command}'
        
        builder = ArtBuilder.LeaderboardBuilder(self.bot)
        loop = asyncio.get_event_loop()
        loop.create_task(
            builder.async_set_leaderboard_images(loop, first_message, second_message, leaderb, command)
        )



    @app_commands.command(
        name="statistic",
        description="How many times did a user use a feature",
        extras={'cog': 'stats'}
    )
    @app_commands.describe(user="Welke persoon")
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=1, per=10, key=lambda i: (i.guild_id, i.user.id))
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
        view = CommandView(self.bot, is_leaderboard=False)
        await interaction.response.send_message(view=view)
        await view.wait()

        # timeout
        if view.chosen_command is None:
            raise TimeoutCommand("Timeout in /statistic")

        #  generate response
        embed = await self.get_stat_individual_embed(user, view.chosen_command)
        
        await interaction.edit_original_response(embed=embed, view=None)



    @app_commands.command(
        name="fortnite",
        description="See statistic about a fortnite creative map",
        extras={'cog': 'stats'}
    )
    @app_commands.choices(map=[
        discord.app_commands.Choice(name="Naruto Box PVP", value="3216-2522-9844"),
        discord.app_commands.Choice(name="📦STARWARS BOX PVP🔥", value="1630-9217-6519"),
    ])   
    @checks.not_blacklisted()
    async def fortnite(self, interaction, map: discord.app_commands.Choice[str]) -> None:
        await interaction.response.defer()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(f"https://fortnite.gg/island?code={map.value}", headers=headers)

        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            embed = embeds.DefaultEmbed(
                f'🎮 {map.name}', map.value
            )

            player_stats_titles = soup.find_all('div', class_='chart-stats-title')

            embed.add_field(name="Players Right Now", value=f"```{player_stats_titles[0].text}```")
            embed.add_field(name="All Time Peak", value=f"```{player_stats_titles[2].text}```")

            embed.set_image(url=str(soup.find(id='island-img')["src"]))

            await interaction.followup.send(embed=embed)

        else:
            return interaction.followup.send(embed=embeds.OperationFailedEmbed(
                "Something went wrong", response.status_code
            ))



    async def get_stat_individual_embed(self, user, command):
        """Get an embed for individual stats

        Args:
            userid (str): Id of user 
            command (str): Which command

        Returns:
            Embed
        """
        if command == "bancount":
            count = await db_manager.get_ban_count(user.id)
        
        elif command == "ban_gamble_all":
            return await self.get_embed_ban_gamble_all(user)
        
        elif command == "current_win_streak":
            count = await db_manager.get_current_win_streak(user.id)

        elif command == "current_loss_streak":
            count = await db_manager.get_current_loss_streak(user.id)

        elif command == "highest_win_streak":
            count = await db_manager.get_highest_win_streak(user.id)

        elif command == "highest_loss_streak":
            count = await db_manager.get_highest_loss_streak(user.id)

        elif command == "ban_total_wins":
            count = await db_manager.get_ban_total_wins(user.id)

        elif command == "ban_total_losses":
            count = await db_manager.get_ban_total_losses(user.id)

        else:
            # krijg count bericht uit db
            count = await db_manager.get_command_count(user.id, command)

        
        # Geen berichten
        if len(count) == 0 or int(count[0][0]) == 0:
            if command == "bancount":
                title = f"🔨 <@{user.display_name}> has not been banned yet."

            elif command == "current_win_streak":
                title = f"🏆 <@{user.display_name}> doesn't have a win streak yet."

            elif command == "current_loss_streak":
                title = f"🤓 <@{user.display_name}> doesn't have a loss streak yet."

            elif command == "highest_win_streak":
                title = f"🏆 <@{user.display_name}> doesn't have a highest win streak yet."

            elif command == "highest_loss_streak":
                title = f"🤓 <@{user.display_name}> doesn't have a highest loss streak yet."

            elif command == "ban_total_wins":
                title = f"🏆 <@{user.display_name}> doesn't have a win yet."

            elif command == "ban_total_losses":
                title = f"🤓 <@{user.display_name}> doesn't have a loss yet."

            else:
                title = f"❌ <@{user.display_name}> didn't use /{command} yet."

            return embeds.OperationFailedEmbed(title, emoji=None)
        
        # error
        if count[0] == -1:
            return embeds.OperationFailedEmbed(
                "Something went wrong...", count[1]
            )
        
        if command == "messages_played":
            desc = f"**<@{user.id}> played```{count[0][0]}``` messages.**"

        elif command == "messages_deleted":
            desc = f"**<@{user.id}> deleted```{count[0][0]}``` messages.**"

        elif command == "bancount":
            desc = f"🔨 **<@{user.id}> has been banned ```{count[0][0]}``` times.**"
        
        elif command == "current_win_streak":
            desc = f"🏆 **<@{user.id}> has a current win streak of ```{count[0][0]}```**"

        elif command == "current_loss_streak":
            desc = f"**<@{user.id}> has a current loss streak of ```{count[0][0]}```**"

        elif command == "highest_win_streak":
            desc = f"🏆 **<@{user.id}> has a highest win streak of ```{count[0][0]}```**"

        elif command == "highest_loss_streak":
            desc = f"**<@{user.id}> has a highest loss streak of ```{count[0][0]}```**"

        elif command == "ban_total_wins":
            desc = f"🏆 **<@{user.id}> total wins```{count[0][0]}```**"

        elif command == "ban_total_losses":
            desc = f"**<@{user.id}> total losses ```{count[0][0]}```**" 
        
        else:
            desc = f"**<@{user.id}> used {command} ```{count[0][0]}``` times.**"

        return embeds.DefaultEmbed(
            "📊 Individual Statistic", desc, user=user
        )


    async def get_embed_ban_gamble_all(self, user):
        embed = embeds.DefaultEmbed(
            "📊 Ban Gamble Statistic", user=user
        )
        counts = []
        counts.append(("🏆 Total wins", await db_manager.get_ban_total_wins(user.id))) 
        counts.append(("😔 Total losses", await db_manager.get_ban_total_losses(user.id))) 
        counts.append(("☯️ K/D ratio", await db_manager.get_ban_kd_ratio(user.id)))
        counts.append(("📈 Highest win streak", await db_manager.get_highest_win_streak(user.id)))
        counts.append(("📉 Highest loss streak", await db_manager.get_highest_loss_streak(user.id))) 
        counts.append(("🏅 Current win streak", await db_manager.get_current_win_streak(user.id)))
        counts.append(("😓 Current loss streak", await db_manager.get_current_loss_streak(user.id)))
        
        for title, count in counts:

            if len(count) != 0 and int(float(count[0][0])) != 0:
                embed.add_field(
                    name=title,
                    value=f"```{count[0][0]}```",
                )


        return embed




class CommandView(View):
    def __init__(self, bot, is_leaderboard) -> None:
        super().__init__(timeout=60)
        self.bot = bot
        self.is_leaderboard = is_leaderboard
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
        command_select = CommandSelect(self.bot, select_item.values[0], self.is_leaderboard)

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
        await interaction.message.edit(view=None, embed=embeds.DefaultEmbed(
            "⏳ Loading...", "This can take a while."
        ))

        await interaction.response.defer()
        self.stop()


class CommandSelect(Select):
    def __init__(self, bot, selected_cog, is_leaderboard):

        self.is_leaderboard = is_leaderboard

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

            if self.is_leaderboard:
                commands.append(("Ban Gamble - Current Win Streak", "current_win_streak"))
                commands.append(("Ban Gamble - Current Loss Streak", "current_loss_streak"))
                commands.append(("Ban Gamble - Ratio", "ban_gamble_ratio"))
                commands.append(("Ban Gamble - Highest Win Streak", "highest_win_streak"))
                commands.append(("Ban Gamble - Highest Loss Streak", "highest_loss_streak"))
                commands.append(("Ban Gamble - Total Wins", "ban_total_wins"))
                commands.append(("Ban Gamble - Total Losses", "ban_total_losses"))
            else:
                commands.append(("Ban Gamble - Statistics", "ban_gamble_all"))

        super().__init__(
            placeholder="Pick a feature", 
            options=[SelectOption(label=label, value=value) for label, value in commands]
        )


    async def callback(self, interaction:Interaction):
        await self.view.respond_to_answer2(interaction, self.values)



async def setup(bot):
    await bot.add_cog(Stats(bot))
