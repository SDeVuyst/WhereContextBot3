""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
import os
import random
from discord import app_commands
from discord.ext import commands
from helpers import checks, db_manager, PodiumBuilder
from discord.ext.commands import has_permissions
from datetime import datetime
from exceptions import CogLoadError

class Admin(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.bot = bot

    conmand_cog_group = app_commands.Group(name="cog", description="Cog Group")
    blacklist_group = app_commands.Group(name="blacklist", description="Blacklist Group")
    


    @app_commands.command(name="status", description="Set the status of the bot for 1 hour (10🪙)", extras={'cog': 'admin'})
    @app_commands.checks.cooldown(rate=1, per=300) # 1 per 5 minutes
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @checks.cost_nword(10)
    @app_commands.describe(status="What do you want the status of the bot to be")
    async def status(self, interaction, status: app_commands.Range[str, 1, 50]) -> None:
        """Set the status of the bot

        Args:
            interaction (Interaction): Users Interaction
            status (app_commands.Range[str, 1, 50]): status
        """

        await interaction.response.defer()

        # set the status
        self.bot.statusManual = datetime.now()
        await self.bot.change_presence(activity=discord.Game(status))

        embed = discord.Embed(
            title="✅ Status changed!",
            description=f"Changed status to ```{status}```",
            color=self.bot.succesColor
        )

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -10)
        
        # send response
        await interaction.followup.send(embed=embed)


    
    @app_commands.command(name="anti_gif", description="Prevent a user from using gifs for 1 hour (125🪙)", extras={'cog': 'admin'})
    @app_commands.checks.cooldown(rate=1, per=30) # 1 per 30 sec
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @checks.cost_nword(125)
    @app_commands.describe(user="Who to block")
    async def anti_gif(self, interaction, user: discord.User) -> None:
        """Prevent a user from using gifs for 1 hour

        Args:
            interaction (Interaction): Users Interaction
            user (User): who to block
        """

        await interaction.response.defer()

        # add user to block list
        self.bot.gif_prohibited.append(
            (user.name, datetime.now())
        )

        embed = discord.Embed(
            title="✅ Done!",
            description=f"<@{user.id}> is now banned from using gifs.",
            color=self.bot.succesColor
        )

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -125)

        # stuur het antwoord
        await interaction.followup.send(embed=embed)



    @app_commands.command(name="lien",description="LIEN LOCKDOWN (admin only)", extras={'cog': 'admin'})
    @has_permissions(ban_members=True)
    @app_commands.checks.cooldown(rate=1, per=180)
    @checks.not_in_dm()
    @checks.not_blacklisted()
    async def lien(self, interaction) -> None:
        """Kicks Jerome in case of emergency

        Args:
            interaction (Interaction): Users Interaction
        """

        # kick grom
        try:
            gromID = int(os.environ.get("GROM"))
            grom = await interaction.guild.fetch_member(gromID)
            await grom.kick(reason=":warning: ***LIEN LOCKDOWN*** :warning:")

            embed = discord.Embed(
                title=":warning: ***LIEN LOCKDOWN*** :warning:",
                description="<@464400950702899211> has been kicked.",
                color=self.bot.errorColor
            )
        # grom kick error
        except:
            embed = discord.Embed(
                title=":warning: ***LIEN LOCKDOWN*** :warning:",
                description="<@464400950702899211> is not in the server.",
                color=self.bot.errorColor
            )

        # stuur lockdown bericht
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="sync",
        description="Synchronizes the slash commands (admin only)",
        extras={'cog': 'admin'}
    )
    @app_commands.describe(scope="The scope of the sync.")
    @app_commands.choices(scope=[
        discord.app_commands.Choice(name="Global", value="global"),
        discord.app_commands.Choice(name="Server", value="server"),
    ])
    @checks.is_owner()
    async def sync(self, interaction, scope: discord.app_commands.Choice[str]) -> None:
        """Synchronizes the slash commands

        Args:
            interaction (Interaction): Users interaction
            scope (discord.app_commands.Choice[str]): The scope to sync, can be global or server
        """
        await interaction.response.defer()

        if scope.value == "global":
            cmds = await self.bot.tree.sync()
            self.bot.save_ids(cmds)

            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=self.bot.succesColor,
            )
            await interaction.followup.send(embed=embed)
            return
        
        elif scope.value == "server":

            # context.bot.tree.copy_global_to(guild=context.guild)
            cmds = await self.bot.tree.sync(guild=interaction.guild)
            self.bot.save_ids(cmds)

            embed = discord.Embed(
                description="Slash commands have been synchronized in this server.",
                color=self.bot.succesColor,
            )
            await interaction.followup.send(embed=embed)
            return
        
        embed = discord.Embed(
            description="The scope must be `global` or `server`.", color=self.bot.errorColor
        )
        await interaction.followup.send(embed=embed)



    @conmand_cog_group.command(
        name="load",
        description="Load a cog (admin only)",
        extras={'cog': 'admin', 'prefix': 'cog'}
    )
    @app_commands.describe(cog="The name of the cog to load")
    @checks.is_owner()
    async def load_cog(self, interaction, cog: str) -> None:
        """Load a given cog

        Args:
            interaction (Interaction): users interaction
            cog (str): The cog to load
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            self.bot.loaded.add(cog)
            self.bot.unloaded.discard(cog)
        except Exception:
            raise CogLoadError(cog, 0)
        
        embed = discord.Embed(
            description=f"Successfully loaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await interaction.response.send_message(embed=embed)



    @conmand_cog_group.command(
        name="unload",
        description="Unloads a cog (admin only)",
        extras={'cog': 'admin', 'prefix': 'cog'}
    )
    @app_commands.describe(cog="The name of the cog to unload")
    @checks.is_owner()
    async def unload_cog(self, interaction, cog: str) -> None:
        """Unloads a cog

        Args:
            interaction (Interaction): Users Interaction
            cog (str): The cog to unload
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            self.bot.loaded.discard(cog)
            self.bot.unloaded.add(cog)
        except Exception:
            raise CogLoadError(cog, 1)
        embed = discord.Embed(
            description=f"Successfully unloaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await interaction.response.send_message(embed=embed)


    @conmand_cog_group.command(
        name="reload",
        description="Reloads a cog (admin only)",
        extras={'cog': 'admin', 'prefix': 'cog'}
    )
    @app_commands.describe(cog="The name of the cog to reload")
    @checks.is_owner()
    async def reload_cog(self, interaction, cog: str) -> None:
        """Reloads a cog

        Args:
            interaction (Interaction): Users interaction
            cog (str): The cog to reload
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        
        except Exception:
            raise CogLoadError(cog, 2)

        embed = discord.Embed(
            description=f"Successfully reloaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await interaction.response.send_message(embed=embed)


    @conmand_cog_group.command(
        name="all",
        description="See loaded/unloaded cogs (admin only)",
        extras={'cog': 'admin', 'prefix': 'cog'}
    )
    @checks.is_owner()
    async def all(self, interaction) -> None:
        """Shows which cogs are loaded/unloaded

        Args:
            interaction (Interaction): users interaction
        """
        
        embed = discord.Embed(
            title="Cog info",
            color=self.bot.defaultColor
        )
        loaded_fields = "\n".join(list(self.bot.loaded))
        embed.add_field(
            name="Loaded", value=f'```\n{loaded_fields}```', inline=False
        )

        unloaded_fields = "\n".join(list(self.bot.unloaded))
        if len(unloaded_fields) > 0:
            embed.add_field(
                name="Unloaded", value=f"```\n{unloaded_fields}```", inline=False
            )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="restart",
        description="Make the bot restart (admin only)",
        extras={'cog': 'admin'}
    )
    @checks.is_owner()
    async def restart(self, interaction) -> None:
        """Restarts the bot

        Args:
            interaction (Interaction): Users Interaction
        """
        embed = discord.Embed(description="Restarting. brb :wave:", color=self.bot.defaultColor)
        await interaction.response.send_message(embed=embed)

        # We shut down the bot, but heroku will automatically restart it.
        await self.bot.close()
        


    @blacklist_group.command(
        name="show",
        description="Shows the list of all blacklisted users (admin only)",
        extras={'cog': 'admin', 'prefix': 'blacklist'}
    )
    @checks.is_owner()
    async def blacklist_show(self, interaction) -> None:
        """Shows list of all blacklisted users

        Args:
            interaction (Interaction): Users Interaction
        """
        blacklisted_users = await db_manager.get_blacklisted_users()
        
        # Geen blacklisted users
        if len(blacklisted_users) == 0:
            embed = discord.Embed(
                description="There are currently no blacklisted users.", color=self.bot.defaultColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # error
        elif blacklisted_users[0] == -1:
            raise Exception(blacklisted_users[1])

        # alles is ok
        embed = discord.Embed(title="Blacklisted Users", color=self.bot.defaultColor)
        users = []
        for bluser in blacklisted_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(
                int(bluser[0])
            )
            users.append(f"• {user.mention} ({user}) - Blacklisted at {bluser[1].strftime('%d/%m/%Y - %H:%M:%S')}")
        embed.description = "\n".join(users)
        await interaction.response.send_message(embed=embed)



    @blacklist_group.command(
        name="add",
        description="Lets you add a user from not being able to use the bot (admin only)",
        extras={'cog': 'admin', 'prefix': 'blacklist'}
    )
    @app_commands.describe(user="The user that should be added to the blacklist")
    @checks.is_owner()
    async def blacklist_add(self, interaction, user: discord.User) -> None:
        """Adds a user to the blacklist

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user to add
        """
        user_id = user.id
        if await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is already in the blacklist.",
                color=self.bot.errorColor,
            )
            await interaction.response.send_message(embed=embed)
            return
        total = await db_manager.add_user_to_blacklist(user_id)

        # error
        if total == -1:
            raise Exception("Kon geen verbinding maken met de databank.")
        
        # alles oke
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully added to the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await interaction.response.send_message(embed=embed)



    @blacklist_group.command(
        name="remove",
        description="Lets you remove a user from not being able to use the bot (admin only)",
        extras={'cog': 'admin', 'prefix': 'blacklist'}
    )
    @app_commands.describe(user="The user that should be removed from the blacklist.")
    @checks.is_owner()
    async def blacklist_remove(self, interaction, user: discord.User) -> None:
        """Removes a user from the blacklist

        Args:
            interaction (Interaction): Users interaction
            user (discord.User): Which user to remove
        """
        user_id = user.id
        if not await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is not in the blacklist.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        total = await db_manager.remove_user_from_blacklist(user_id)

        #error
        if total == -1:
            raise Exception('Kon geen verbinding maken met de databank.')
        
        # alles ok
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully removed from the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="unban",
        description="Unban a user (500🪙)",
        extras={'cog': 'admin'}
    )
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=2, per=3600)
    @checks.cost_nword(500)
    async def unban(self, interaction) -> None:
        """Unban a user

        Args:
            interaction (Interaction): Users Interaction
        """
        guild = await self.bot.fetch_guild(int(os.environ.get("GUILD_ID")))
        bans = [entry async for entry in guild.bans(limit=25)]
        if len(bans) > 0:
            await interaction.response.send_message(view=UnbanView(bans, self.bot))
        else:
            embed = discord.Embed(
                description=f"No banned users..", color=self.bot.defaultColor
            )
            await interaction.response.send_message(embed=embed)

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -500)


    
    @app_commands.command(
        name="nickname",
        description="Set the nickname of a user",
        extras={'cog': 'admin'}
    )
    @checks.not_blacklisted()
    @app_commands.describe(user="Which user")
    @app_commands.describe(nickname="What nickname")
    async def nickname(self, interaction, user: discord.User, nickname: app_commands.Range[str, 1, 32]) -> None:
        """Set the nickname of a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user
            nickname (str): what nickname
        """
        
        await user.edit(nick=nickname)
        embed = discord.Embed(
            title='✅ Done',
            description=f"{user} is now called {nickname}",
            color=self.bot.succesColor
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="invite", description="Create an invite", extras={'cog': 'admin'})
    @checks.not_blacklisted()
    async def invite(self, interaction) -> None:
        """Send an invite to the main server

        Args:
            interaction (Interaction): Users Interaction
        """
        
        
        guild = await self.bot.fetch_guild(int(os.environ.get("GUILD_ID")))
        channel = await guild.fetch_channel(int(os.environ.get("CHANNEL")))

        # unban the user
        if os.environ.get("AUTOUNBAN") == "True":
            try:
                await guild.unban(interaction.user)
                await interaction.user.send("I unbanned you.")
            except:
                pass

        link = await channel.create_invite(max_age = 0, max_uses = 1)

        await interaction.response.send_message(link)



    @app_commands.command(name="profile", description="See someones profile", extras={'cog': 'admin'})
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=1, per=10)
    @app_commands.describe(user="Which user")
    async def profile(self, interaction, user: discord.User=None) -> None:
        """View someones bot profile

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user
        """
        await interaction.response.defer()

        # geen gebruiker meegegeven, gaat over zichzelf
        if user is None:
            user = interaction.user

        # creeer embed
        embed = discord.Embed(
            title=f"**{user.display_name}'s Profile**",
            color=self.bot.defaultColor,
            timestamp=datetime.utcnow()
        )

        # set thumbnail als users character
        embed.set_thumbnail(
            url=str(user.avatar.url)
        )

        embed.set_author(
            name=user.name, 
            icon_url=str(user.avatar.url)
        )

        nick = await db_manager.get_nickname(interaction.guild_id, user.id)
        embed.add_field(
            name="📛 Default Nickname",
            value="```None```" if nick in [-1, None] else f"```{nick[0]}```",
            inline=False
        )

        ncount = await db_manager.get_nword_count(user.id)
        embed.add_field(
            name="🥷🏿 N-Count",
            value=f"```{normalizeCount(ncount)}```",
            inline=True
        )

        bancount = await db_manager.get_ban_count(user.id)
        embed.add_field(
            name="🔨 Amount of Bans",
            value=f"```{normalizeCount(bancount)}```",
            inline=True
        )

        # get most used command
        commandcount = await db_manager.get_most_used_command(user.id)
        if commandcount is None or commandcount[0] == -1:
            value = f"```No Commands Used```"
        else:
            com = "Danae Trigger" if commandcount[0] == 'danae' else f"/{commandcount[0]}"
            value=f"```{com}: {commandcount[1]}```"

        embed.add_field(
            name="🤖 Most Used Command",
            value=value,
            inline=False
        )

        # get total amount of commands used
        totalcommandcount = await db_manager.get_total_used_command(user.id)
        totalcommandcountvalue = 0 if (totalcommandcount is None or totalcommandcount[0] == -1) else totalcommandcount[0]
        embed.add_field(
            name="🗒️ Total Commands Used",
            value=f"```{totalcommandcountvalue}```",
            inline=False
        )

        # show podiums if user has one
        builder = PodiumBuilder.PodiumBuilder(self.bot)
        if builder.userHasPodium(user.id):
            file = await builder.getAllPodiumsImage([user.id, user.id, user.id], padding=100, add_characters=False)
            embed.set_image(url="attachment://podium.png")
        
            return await interaction.followup.send(embed=embed, files=[file], view=ConfigureView(self.bot, embed, user.id))

        await interaction.followup.send(embed=embed, view=ConfigureView(self.bot, embed, user.id))


class UnbanView(discord.ui.View):
    def __init__(self, bans, bot):
        super().__init__()
        self.add_item(UnbanDropdown(bans, bot))



class UnbanDropdown(discord.ui.Select):
    def __init__(self, bans, bot):
        self.bot = bot
        options = [discord.SelectOption(label=ban.user.global_name, value=str(ban.user.id)) for ban in bans]
        super().__init__(placeholder="Pick a user to unban", options=options, min_values=1, max_values=1)

    async def callback(self, interaction):
        guild = await self.bot.fetch_guild(int(os.environ.get("GUILD_ID")))
        user = await self.bot.fetch_user(int(self.values[0]))

        await guild.unban(user)
        embed = discord.Embed(
            title='✅ Done',
            description=f"{user} is now unbanned",
            color=self.bot.succesColor,
        )
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.defer()


    
class ConfigureView(discord.ui.View):
    def __init__(self, bot, embed, user_id):
        self.bot = bot
        self.embed = embed
        self.nickname = 'None'
        self.user_id = int(user_id)

        super().__init__(timeout=500)


    @discord.ui.button(label="Set default nickname", emoji='📜', style=discord.ButtonStyle.blurple, disabled=False)
    async def add_nickname(self, interaction: discord.Interaction, button: discord.ui.Button):
        # send modal
        modal = AddNicknameModal(self)
        await interaction.response.send_modal(modal)

        # wait till modal finishes
        await modal.wait()

        # save the nickname
        await db_manager.set_nickname(interaction.guild_id, self.user_id, self.nickname)

        # set description to embed
        self.embed.set_field_at(index=0, name="📛 Default Nickname", value=f"```{self.nickname}```", inline=False)

        # edit config embed
        msg = await interaction.original_response()
        await msg.edit(embed=self.embed, view=self)


    @discord.ui.button(label="Set default roles", emoji='📝', style=discord.ButtonStyle.blurple, disabled=False)
    async def add_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        autoroles = await db_manager.get_autoroles(interaction.guild_id, self.user_id)
        if autoroles is not None:
            autoroles = [int(role_id) for role_id in autoroles[0]]
        else:
            autoroles = []

        embed = discord.Embed(
            title="📝 Select your default roles",
            description="""Please select which roles you want to have automatically added when you join this server.\n
            Note that you can do this for every server WCB3 is in, and can only select roles lower than your current role.\n""",
            color=self.bot.defaultColor
        )

        await interaction.response.send_message(
            embed=embed,
            view=RolesSelectView(
                interaction.guild.get_member(self.user_id), 
                await interaction.guild.fetch_roles(), 
                self.bot,
                autoroles
            )
        )

    
    @discord.ui.button(label="Set Character Poses", emoji='👥', style=discord.ButtonStyle.blurple, disabled=False)
    async def set_pose(self, interaction: discord.Interaction, button: discord.ui.Button):
        builder = PodiumBuilder.PodiumBuilder(self.bot)
        file = await builder.getAllPosesImage(self.user_id)
        amountOfPoses = builder.getAmountOfPoses(self.user_id)

        # get previously selected poses
        selectedPoses = []
        for i in range(1, 4):
            poses = await db_manager.get_poses(self.user_id, i)
            if poses is not None:
                poses = [int(pose) for pose in poses[0]]
            else:
                poses = []
            selectedPoses.append(poses)

        embed = discord.Embed(
            title="👥 Select your Poses",
            description="""You can pick different poses for each position on your podium.\n
            If you select multiple poses, one will be selected at random every time your podium is displayed.""",
            color=self.bot.defaultColor
        )
        embed.set_image(url="attachment://poses.png")

        await interaction.response.send_message(
            embed=embed,
            view=PosesSelectView(
                self.bot,
                amountOfPoses,
                selectedPoses,
                interaction.guild.get_member(self.user_id), 
            ),
            files=[file]
        )


    async def interaction_check(self, interaction: discord.Interaction):
        """Check that the user is the one who is clicking buttons
k
        Args:
            interaction (discord.Interaction): Users Interaction

        Returns:
            bool
        """
        responses = [
            f"<@{interaction.user.id}> shatap lil bro", 
            f"<@{interaction.user.id}> you are NOT him",
            f"<@{interaction.user.id}> blud thinks he's funny",
            f"<@{interaction.user.id}> imma touch you lil nigga",
            f"<@{interaction.user.id}> it's on sight now",
        ]

        try:
            is_possible = (interaction.user.id == self.user_id) or str(interaction.user.id) in list(os.environ.get("OWNERS").split(","))
            if not is_possible:
                await interaction.response.send_message(random.choice(responses))
            return is_possible
        
        except:
            return False
        


class AddNicknameModal(discord.ui.Modal, title='Set default nickname'):

    def __init__(self, configure_view):
        self.configure_view = configure_view
        super().__init__(timeout=None)
    
    # nickname input
    answer = discord.ui.TextInput(
        label='Nickname', 
        required=True,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        # save value
        self.configure_view.nickname = self.answer.value

        # respond to user
        embed = discord.Embed(
            title="💾Default nickname set!",
            description=f'```{self.answer.value}```',
            color=self.configure_view.bot.succesColor
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)



class RolesSelectView(discord.ui.View):
    def __init__(self, user, all_roles, bot, autoroles, timeout = 180):
        self.user = user
        self.all_roles = all_roles
        self.bot = bot
        self.selectedRoles = None
        
        super().__init__(timeout=timeout)
        self.add_item(RolesSelect(user, all_roles, bot, self, autoroles))    

    # a cancel button
    # will keep the message but remove the view and replace the text with "Cancelled"
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"Cancelled!",
            color=self.bot.defaultColor,
        )
        await interaction.response.edit_message(embed=embed, view=None, delete_after=10)


    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=False, emoji='✅')
    async def submit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # defer in case processing the selected data takes a while
        await interaction.response.defer()
        selected_roles = [discord.utils.get(self.all_roles, name=role) for role in self.selectedRoles]

        # save roles in db
        succes = await db_manager.set_autoroles(
            interaction.guild_id,
            self.user.id,
            [str(role.id) for role in selected_roles]
        )

        if not succes:
            raise Exception("Could not save roles to db.")
        
        # create formatted string representing the selected roles
        formatted_selected_roles = ''
        for role in selected_roles:
            formatted_selected_roles += role.mention + '\n'

        desc = f"Your new AutoRoles are now:\n{formatted_selected_roles}" if len(selected_roles) > 0 else "You don't have any autoroles set for this server."
        embed = discord.Embed(
            title=f"✅ Edited default Roles!",
            description=desc,
            color=self.bot.succesColor,
        )
        
        await interaction.edit_original_response(embed=embed, view=None)



class RolesSelect(discord.ui.Select):
    def __init__(self, user, all_roles, bot, view, autoroles):
        self.bot = bot
        self.roleView = view

        # get available roles for the user
        highest_role = discord.utils.find(lambda role: role in all_roles, reversed(user.roles))
        available_roles = [role for role in all_roles if role <= highest_role]
        available_roles = list(filter(lambda r: r.name != '@everyone', available_roles))

        # generate the options
        options = [discord.SelectOption(label=role.name, default=role.id in autoroles) for role in available_roles[:25]]

        super().__init__(placeholder="Select an option", max_values=len(options), min_values=0, options=options)


    async def callback(self, interaction: discord.Interaction):
        self.roleView.selectedRoles = self.values
        await interaction.response.defer()



class PosesSelectView(discord.ui.View):
    def __init__(self, bot, amountOfPoses, selectedPoses, user, timeout = 180):
        self.bot = bot
        self.amountOfPoses = amountOfPoses
        self.selectedPoses = selectedPoses
        self.user = user
        
        super().__init__(timeout=timeout)
        self.add_item(PosesSelect(self, bot, amountOfPoses, selectedPoses[0], user, 1))
        self.add_item(PosesSelect(self, bot, amountOfPoses, selectedPoses[1], user, 2))    
        self.add_item(PosesSelect(self, bot, amountOfPoses, selectedPoses[2], user, 3))        

    # a cancel button
    # will keep the message but remove the view and replace the text with "Cancelled"
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"Cancelled!",
            color=self.bot.defaultColor,
        )
        await interaction.response.edit_message(embed=embed, view=None, delete_after=10, attachments=[])


    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=False, emoji='✅')
    async def submit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # defer in case processing the selected data takes a while
        await interaction.response.defer()
        
        for place in range(1, 4):

            poses = [int(i) for i in self.selectedPoses[place-1]]
            if len(poses) > 0:
                # save poses in db
                succes = await db_manager.set_poses(
                    self.user.id,
                    poses,
                    place
                )
            
            else:
                # user removed the active poses
                succes = await db_manager.remove_poses(
                    self.user.id,
                    place
                )

            if not succes:
                raise Exception("Could not save poses to db.")

        embed = discord.Embed(
            title=f"✅ Saved active poses!",
            color=self.bot.succesColor,
        )
        
        await interaction.edit_original_response(embed=embed, view=None)



class PosesSelect(discord.ui.Select):
    def __init__(self, view, bot, amountOfPoses, selectedPoses, user, place):
        self.poseView = view
        self.bot = bot
        self.amountOfPoses = amountOfPoses
        self.selectedPoses = selectedPoses
        self.user = user
        self.place = place

        # generate the options
        options = [
            discord.SelectOption(
                label=f"Pose {i+1}", default=i+1 in selectedPoses, value=i+1
            ) for i in range(amountOfPoses)
        ]

        # readable format
        places = ["1st", "2nd", "3rd"]

        super().__init__(
            placeholder=f"Select your active poses ({places[place-1]} Place)", 
            max_values=amountOfPoses, 
            min_values=0, 
            options=options
        )


    async def callback(self, interaction: discord.Interaction):
        # save the selected poses
        poses = [1,0,2]
        self.poseView.selectedPoses[poses[self.place-1]] = self.values
        await interaction.response.defer()



async def setup(bot):
    await bot.add_cog(Admin(bot))



# gives correct int based off db output
def normalizeCount(count):
    if len(count) == 0 or int(count[0][0]) == 0 or count[0] == -1:
        return 0
    else:
        return count[0][0]