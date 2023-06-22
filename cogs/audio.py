
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Context
import discord
import asyncio
from helpers import checks, db_manager


# Here we name the cog and create a new class for the cog.
class Audio(commands.Cog, name="audio"):
    def __init__(self, bot):
        self.bot = bot
        self.isConnected = False

    @commands.hybrid_command(name="join", description="bot joins voice channel")
    @checks.not_blacklisted()
    async def join(self, context: Context):
        try:
            if not context.message.author.voice:
                embed = discord.Embed(
                    title=f"You are not in a voice channel",
                    color=0xE02B2B
            ) 
            else:
                channel = context.author.voice.channel
                await channel.connect()
                embed = discord.Embed(
                    title=f"Joined channel {channel.name}!",
                    color=0x39AC39
                )
        except discord.ClientException:
            embed = discord.Embed(
                title=f"Already in voice channel",
                color=0xE02B2B
            )
            
        await context.send(embed=embed)
        self.isConnected = True
    
        

    @commands.hybrid_command(name="leave", description="bot leaves voice channel")
    @checks.not_blacklisted()
    async def leave(self, context: Context):

        voice_client = context.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            embed = discord.Embed(
                title=f"left channel!",
                color=0x39AC39
            )
            await context.send(embed=embed)

        else:
            embed = discord.Embed(
                title=f"You are not in a voice channel",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        
        self.isConnected = False
        

    @commands.hybrid_command(name="soundboard", description="Play effect from soundboard")
    @app_commands.choices(effect=[
        discord.app_commands.Choice(name="hentai Xander", value="hentai.mp3"),
        discord.app_commands.Choice(name="alexa... shut the fuck up", value="alexa.mp3"),
        discord.app_commands.Choice(name="yeah boy", value="yeah-boy.mp3"),
        discord.app_commands.Choice(name="sinister laugh", value="sinister-laugh.mp3"),
        discord.app_commands.Choice(name="help me n-", value="help-me.mp3"),
        discord.app_commands.Choice(name="illuminati", value="illuminati.mp3"),
        discord.app_commands.Choice(name="gta v wasted", value="gta-wasted.mp3"),
        discord.app_commands.Choice(name="surprise motherfucker", value="surprise.mp3"),
        discord.app_commands.Choice(name="the rock boom sound", value="the-rock.mp3"),
        discord.app_commands.Choice(name="ba laughing", value="ba-lach.mp3"),
    ])
    @checks.not_blacklisted()
    async def soundboard(self, context: Context, effect: discord.app_commands.Choice[str]):
    
        try:
            if not self.isConnected:
                await context.invoke(self.bot.get_command('join'))

            server = context.message.guild
            vc = server.voice_client
            vc.play(discord.FFmpegPCMAudio(f"{os.path.realpath(os.path.dirname(__file__))}/../audio_snippets/{effect.value}"))
            embed = discord.Embed(
                title=f"played {effect.name}!",
                color=0x39AC39
            )
            await context.send(embed=embed, ephemeral=True)

            # stats
            await db_manager.increment_or_add_command_count(context.author.id, "soundboard", 1)

        except Exception as e:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=e,
                color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Audio(bot))