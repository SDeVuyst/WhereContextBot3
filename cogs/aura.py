""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""



import discord
from discord import app_commands
from discord.ext import commands

import embeds

from helpers import checks, db_manager, pagination



class Aura(commands.Cog, name="aura"):
    def __init__(self, bot):
        self.bot = bot



    @app_commands.command(name="aura", description=f"See the aura of a person", extras={'cog': 'aura'})
    @checks.not_blacklisted()
    async def aura(self, interaction, user: discord.User = None) -> None:

        await interaction.response.defer()

        # geen gebruiker meegegeven, gaat over zichzelf
        if user is None:
            user = interaction.user

        amount = await db_manager.get_total_aura(str(user.id))
        embed = embeds.DefaultEmbed(
            f"💥 Aura of {user.display_name}",
            description=f"```{amount}```",
            user=user
        )

        await interaction.followup.send(embed=embed, view=AuraView(self.bot, user))


    @app_commands.command(name="aura-event", description=f"Add an aura event to a person", extras={'cog': 'aura'})
    @checks.not_blacklisted()
    @checks.is_owner()
    async def aura_event(self, interaction, amount: int, description: str, user: discord.User = None) -> None:

        await interaction.response.defer()

        # geen gebruiker meegegeven, gaat over zichzelf
        if user is None:
            user = interaction.user

        total = await db_manager.add_aura_event(str(user.id), amount, description)

        # error
        if total == -1:
            raise Exception("Kon geen verbinding maken met de databank.")
        
        embed = embeds.OperationSucceededEmbed(
            f"💥 Aura event added!",
            f"{user.mention}: {'+' if amount > 0 else ''}{amount} • {description}"
        )

        await interaction.followup.send(embed=embed)


    
class AuraView(discord.ui.View):
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user
        super().__init__(timeout=500)


    @discord.ui.button(label="See Aura Events", emoji='📆', style=discord.ButtonStyle.blurple, disabled=False)
    async def see_aura_events(self, interaction: discord.Interaction, button: discord.ui.Button):
        async def get_page(page: int):
            L = 5 # elements per page
            embed = embeds.DefaultEmbed(
                f"💥 Aura Events of {self.user.display_name}",
                " ",
                user=self.user
            )
            offset = (page-1) * L

            events = await db_manager.get_all_aura_events(self.user.id)

            # error
            if events[0] == -1:
                events = []

            for event in events[offset:offset+L]:
                embed.description += f"{'+' if event[0] > 0 else ''}{event[0]} • {event[1]}\n"

            n = pagination.Pagination.compute_total_pages(len(events), L)
            embed.set_footer(text=f"Page {page} from {n}")
            return embed, n

        await pagination.Pagination(interaction, get_page).navegate()



async def setup(bot):
    await bot.add_cog(Aura(bot))
