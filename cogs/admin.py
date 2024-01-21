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
from helpers import checks, db_manager
from discord.ext.commands import has_permissions
from datetime import datetime
from exceptions import CogLoadError


class Admin(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.bot = bot

    conmand_cog_group = app_commands.Group(name="cog", description="Cog Group")
    blacklist_group = app_commands.Group(name="blacklist", description="Blacklist Group")
    
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
        try:
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

            

        except discord.HTTPException as e:
            self.bot.logger.warning(e)
            embed = discord.Embed(
                description="HTTPException, most likely daily application command limits.",
                color=self.bot.errorColor,
            )
            await interaction.response.send_message(embed=embed)



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
            embed = discord.Embed(
                description=f"Could not load the `{cog}` cog.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
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
            embed = discord.Embed(
                description=f"Could not unload the `{cog}` cog.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
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
            embed = discord.Embed(
                description=f"Could not reload the `{cog}` cog.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
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
            embed = discord.Embed(
                title=f"Something went wrong",
                description=blacklisted_users[1],
                color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return

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
            embed = discord.Embed(
                description=f"Er is iets misgegaan.",
                color=self.bot.errorColor,
            )
            await interaction.response.send_message(embed=embed)
            return
        
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
            embed = discord.Embed(
                description=f"Er is iets misgegaan.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # alles ok
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully removed from the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await interaction.response.send_message(embed=embed)




    @app_commands.command(name="ban", description="Ban someone", extras={'cog': 'admin'})
    @app_commands.describe(user="Which user")
    @app_commands.describe(reason="Reason for the ban")
    @checks.not_blacklisted()
    async def ban(self, interaction, user: discord.Member, reason: str) -> None:
        """Ban someone

        Args:
            interaction (Interaction): Users Interaction
            user
        """
        await interaction.response.defer()

        banNumberTreshold = 3 # TODO determine amounts of votes needed

        banned_embed = discord.Embed(
            title=f"🔨 You have been banned from {interaction.guild.name}!",
            color=self.bot.defaultColor,
            timestamp=datetime.utcnow()
        )

        banned_embed.add_field(
            name="Reason",
            value=reason,
        )

        doneBanEmbed = discord.Embed(
            title=f"🔨 {user.display_name} has been banned!",
            description=f"Cooked his ass",
            color=self.bot.defaultColor
        )

        # check if user is able to ban, if yes, continue
        # if not, launch vote
        ableToBan = interaction.user.top_role >= user.top_role

        # owner should always be able to ban user
        if str(interaction.user.id) == list(os.environ.get("OWNERS").split(","))[0]:
            ableToBan = True

        if ableToBan:
            # send ban message to user
            await user.send(embed=banned_embed)

            # ban user
            await user.ban(reason=reason, delete_message_days=0)

            # respond to interaction
            await interaction.followup.send(embed=doneBanEmbed)

        else:
            # respond to interaction
            voteEmbed = discord.Embed(
                title=f"🔨 Vote to ban {user.display_name}",
                description=f"This vote succeeds at {banNumberTreshold} votes in favour of banning.\n You have 5 minutes to vote.",
                color=self.bot.defaultColor
            )

            voteEmbed.add_field(name="Reason", value=f"```{reason}```", inline=False)

            voteEmbed.add_field(name="Current votes", value=f"```1/{banNumberTreshold}```")

            await interaction.followup.send(embed=voteEmbed, view=BanView(self.bot, interaction.user.id, user, banNumberTreshold, reason, doneBanEmbed, voteEmbed))



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
    async def nickname(self, interaction, user: discord.User, nickname: str) -> None:
        """Set the nickname of a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user
            nickname (str): what nickname
        """
        try:
            await user.edit(nick=nickname)
            embed = discord.Embed(
                title='✅ Done',
                description=f"{user} is now called {nickname}",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title=f"Er is iets misgegaan.",
                description=e,
                color=self.bot.errorColor
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



class BanView(discord.ui.View):
    def __init__(self, bot, bannerID, user, banNumberTreshold, reason, doneBanEmbed, originalEmbed):
        super().__init__(timeout=300)

        self.bot = bot
        self.user = user
        self.banNumberTreshold = banNumberTreshold
        self.reason = reason
        self.doneBanEmbed = doneBanEmbed
        self.originalEmbed = originalEmbed

        self.peopleWhoVotedYes = [bannerID]


    @discord.ui.button(label="Vote Yes", style=discord.ButtonStyle.danger)
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        # user already voted
        if interaction.user.id in self.peopleWhoVotedYes:
            embed = discord.Embed(
                title="❌ You can't vote twice!",
                color=self.bot.errorColor
            )

        else:
            # add user to voters
            self.peopleWhoVotedYes.append(interaction.user.id)

            embed = discord.Embed(
                title=f"✅ You have voted to kick {self.user.display_name}",
                color=self.bot.succesColor
            )

            # edit original embed
            self.originalEmbed.set_field_at(
                1, name="Current votes", value=f"```{len(self.peopleWhoVotedYes)}/{self.banNumberTreshold}```"
            )
            await interaction.edit_original_response(embed=self.originalEmbed)

        # send response (vote succesful?)
        await interaction.followup.send(embed=embed, ephemeral=True)

        # check if user needs to be banned
        if len(self.peopleWhoVotedYes) >= self.banNumberTreshold:

            # send ban message to user
            banned_embed = discord.Embed(
                title=f"🔨 You have been banned from {interaction.guild.name}!",
                color=self.bot.defaultColor,
                timestamp=datetime.utcnow()
            )

            banned_embed.add_field(
                name="Reason",
                value=f"```{self.reason}```",
            )

            # add field to show who voted
            banned_embed.add_field(
                name="🪦 People who voted for your demise",
                value='\n'.join(
                    [self.bot.get_user(user_id).mention for user_id in self.peopleWhoVotedYes]
                ),
                inline=False                
            )
            await self.user.send(embed=banned_embed)

            # disable original vote
            await interaction.edit_original_response(view=None)

            # send confirmation
            await interaction.followup.send(embed=self.doneBanEmbed)

            # ban user
            await self.user.ban(reason=self.reason, delete_message_days=0)


    @discord.ui.button(label="Remove Vote", style=discord.ButtonStyle.blurple)
    async def remove_vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        # user already voted
        if interaction.user.id not in self.peopleWhoVotedYes:
            embed = discord.Embed(
                title="❌ You didn't vote yet!",
                color=self.bot.errorColor
            )

        else:
            # remove voter from list
            self.peopleWhoVotedYes.remove(interaction.user.id)

            embed = discord.Embed(
                title=f"✅ You have removed your vote to kick {self.user.display_name}",
                color=self.bot.succesColor
            )

            # edit original embed
            self.originalEmbed.set_field_at(
                1, name="Current votes", value=f"```{len(self.peopleWhoVotedYes)}/{self.banNumberTreshold}```"
            )
            await interaction.edit_original_response(embed=self.originalEmbed)
    
        # send response (vote removal succesful?)
        await interaction.followup.send(embed=embed, ephemeral=True)



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

    


async def setup(bot):
    await bot.add_cog(Admin(bot))
