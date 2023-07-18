
import subprocess
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Context
import discord
import asyncio
import tempfile
from helpers import checks, http, ytdl_helper
import yt_dlp as youtube_dl
from pytube import Playlist, YouTube




# Here we name the cog and create a new class for the cog.
class Audio(commands.Cog, name="audio"):
    def __init__(self, bot):
        self.bot = bot

        self.bot_not_in_vc_embed = discord.Embed(
            title=f"Bot is not in vc",
            description="use /join to add bot to vc",
            color=self.bot.errorColor
        ) 

        self.not_playing_embed = discord.Embed(
            title=f"The bot is not playing anything at the moment.",
            description="Use /play to play a song",
            color=self.bot.defaultColor
        )

        self.not_in_vc_embed = discord.Embed(
            title=f"You are not in a voice channel",
            color=self.bot.errorColor
        ) 

        ytdl_format_options = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

        ffmpeg_options = {
            'options': '-vn'
        }

        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

        self.queue = []



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
        discord.app_commands.Choice(name="creeper", value="creeper.mp3"),
    ])
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def soundboard(self, context: Context, effect: discord.app_commands.Choice[str]):

        # check als userin vc zit
        if not context.message.author.voice:
            await context.send(embed=self.not_in_vc_embed)
            return
        try:

            # autojoin vc als bot nog niet in vc zit
            vc = context.message.guild.voice_client
            if not vc.is_connected():
                await context.invoke(self.bot.get_command('join'))

            # pauzeer reeds spelende audio
            if vc.is_playing():
                vc.pause()

            # speel soundboard af
            vc.play(discord.FFmpegPCMAudio(f"{os.path.realpath(os.path.dirname(__file__))}/../audio_snippets/{effect.value}"), 
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(context), self.bot.loop)
            )
            
            # resume de vorige spelende audio
            if vc.is_paused():
                vc.resume()
            
            # confirmatie 
            embed = discord.Embed(
                title=f"played {effect.name}!",
                color=self.bot.succesColor
            )
            await context.send(embed=embed, ephemeral=True)


        except Exception as e:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=e,
                color=self.bot.errorColor
            )
            await context.send(embed=embed, ephemeral=True)



    @commands.hybrid_command(name="tts", description="Text to Speech")
    @app_commands.choices(voice=[
        discord.app_commands.Choice(name="Alexa", value="alexa"),
        discord.app_commands.Choice(name="Peter Griffin", value="peter-griffin"),
        discord.app_commands.Choice(name="Glenn Quagmire", value="quagmire"),
        discord.app_commands.Choice(name="Walter White", value="walter-white"),
        discord.app_commands.Choice(name="Saul Goodman", value="saul-goodman"),
        discord.app_commands.Choice(name="Barack Obama", value="barack-obama"),
        discord.app_commands.Choice(name="DIO (jp)", value="dio-jp"),
        discord.app_commands.Choice(name="PewDiePie", value="pewdiepie"),
        discord.app_commands.Choice(name="Hitler", value="hitler-rant"),
    ])
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    @commands.cooldown(rate=1, per=120)
    async def tts(self, context: Context, speech: str, voice: discord.app_commands.Choice[str]):
        
        # check als user in vc zit
        if not context.message.author.voice:
            await context.send(embed=self.not_in_vc_embed)
            context.command.reset_cooldown(context)
            return
        
        # check als bot in vc zit
        vc = context.message.guild.voice_client
        if vc is None:
            await context.send(embed=self.bot_not_in_vc_embed)
            context.command.reset_cooldown(context)
            return      
            

        await context.defer()

        try:
            # creeer audio file 
            audio_data = await http.query_uberduck(speech, voice.value)
            with tempfile.NamedTemporaryFile(
                suffix=".wav"
            ) as wav_f, tempfile.NamedTemporaryFile(suffix=".opus") as opus_f:
                wav_f.write(audio_data.getvalue())
                wav_f.flush()
                subprocess.check_call(["ffmpeg", "-y", "-i", wav_f.name, opus_f.name])

                self.bot.logger.info(wav_f)
                self.bot.logger.info(opus_f)

                # speel audio af
                source = discord.FFmpegOpusAudio(opus_f.name)

                self.bot.logger.info(source)
                
                if vc.is_playing():
                    vc.pause()

                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(context), self.bot.loop))
                
                while vc.is_playing():
                    await asyncio.sleep(0.5)
                    
                if vc.is_paused():
                    vc.resume()
            
            # confirmatie
            embed = discord.Embed(
                title=f"Said ```{speech}``` in a {voice.name} voice!",
                color=self.bot.succesColor
            )
            await context.interaction.followup.send(embed=embed)


        except Exception as e:
            embed = discord.Embed(
                title=f"Error",
                description=e,
                color=self.bot.errorColor
            )
            await context.interaction.followup.send(embed=embed)



    @commands.hybrid_command(name="play", description="play a youtube video or playlist (use multiple times to add to queue)")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    @app_commands.choices(in_front=[
        discord.app_commands.Choice(name="yes", value=1),
        discord.app_commands.Choice(name="no", value=0),
    ])
    async def play(self, context: Context, youtube_url: str, in_front: discord.app_commands.Choice[int]):

        # check dat user in vc zit
        if not context.message.author.voice:
            await context.send(embed=self.not_in_vc_embed)
            return
        
        # check dat bot in vc zit
        vc = context.message.guild.voice_client
        if vc is None:
            await context.send(embed=self.bot_not_in_vc_embed)
            return  
        
        await context.defer()
        
        try:

            # playlist
            if youtube_url.find("list=") != -1:

                    # krijg afzonderlijke urls van videos in playlist 
                    # voeg de urls toe aan queue
                    desc = ""
                    vid_urls = Playlist(youtube_url)
                    for i, vid_url in enumerate(vid_urls):
                        if in_front.value == 1:
                            self.queue.insert(0, vid_url)
                        else:
                            self.queue.append(vid_url)
                        yt = YouTube(vid_url)

                        if i<10:
                            desc += f"{i+1}: [{yt.title}]({vid_url}) by {yt.author}\n\n"

                    embed = discord.Embed(
                        title=f"Added to Queue",
                        description=desc,
                        color=self.bot.defaultColor
                    )
                    await context.send(embed=embed)
                    
                    if not vc.is_playing():
                        await self.play_next(context)

            # enkele video
            else:
                yt = YouTube(youtube_url)
                
                # voeg lied aan queue toe
                if in_front.value == 1:
                    self.queue.insert(0, youtube_url)
                else:
                    self.queue.append(youtube_url)
                
                # stuur confirmatie dat lied is toegevoegd
                if vc.is_playing():
                    
                    embed = discord.Embed(
                        title=f"Added to Queue",
                        description=f"[{yt.title}]({youtube_url}) by {yt.author}",
                        color=self.bot.defaultColor
                    )
                    await context.interaction.followup.send(embed=embed)
                    return

                await self.play_next(context)
            
        except Exception:
            embed = discord.Embed(
                title=f"Er is iets misgegaan",
                description=f"ben je zeker dat dit een geldige url is?\n{youtube_url}",
                color=self.bot.errorColor
            )
            await context.send(embed=embed)
            return



    @commands.hybrid_command(name="list", description="See the Queue")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def list(self, context: Context):
        
        # lege queue
        if len(self.queue) == 0:
            embed = discord.Embed(
                title=f"Queue is empty!",
                color=self.bot.defaultColor
            )

        # toon lijst van videos in queue
        else:
            desc = ""
            for i, url in enumerate(self.queue):
                if i<10:
                    yt = YouTube(url)
                    desc += f"{i+1}: [{yt.title}]({url}) by {yt.author}\n\n"

            embed = discord.Embed(
                title=f"Queue",
                description=desc,
                color=self.bot.defaultColor
            )

        await context.send(embed=embed)



    @commands.hybrid_command(name="nowplaying", description="See the currently playing track")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def nowplaying(self, context: Context):

        try:
            title="Now playing" if self.track_playing is not None else "Nothing is playing"
            desc = f"[{self.track_playing}]({self.track_playing_url})" if self.track_playing is not None else None
        except:
            title="Nothing is playing"
            desc = None

        embed = discord.Embed(
            title=title,
            description=desc,
            color=self.bot.defaultColor
        )
        await context.send(embed=embed)
      


    @commands.hybrid_command(name="pause", description="Pause currently playing track")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def pause(self, context: Context):

        # check als bot in vc zit
        voice_client = context.message.guild.voice_client
        if voice_client is None:
            await context.send(embed=self.bot_not_in_vc_embed)
            return  
        
        # pauzeer
        if voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(
                title=f"Paused!",
                color=self.bot.succesColor
            )
            await context.send(embed=embed)
        else:
            await context.send(embed=self.not_playing_embed)
      
        

    @commands.hybrid_command(name="resume", description="Resume currently playing track")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def resume(self, context: Context):

        # check als bot in vc zit
        voice_client = context.message.guild.voice_client
        if voice_client is None:
            await context.send(embed=self.bot_not_in_vc_embed)
            return  
        
        # resume
        if voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(
                title=f"Resumed!",
                color=self.bot.succesColor
            )
            await context.send(embed=embed)
        else:
            await context.send(embed=self.not_playing_embed)



    @commands.hybrid_command(name="skip", description="Skip the currently playing track")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def skip(self, context: Context):

        # check als bot in vc zit
        voice_client = context.message.guild.voice_client
        if voice_client is None:
            await context.send(embed=self.bot_not_in_vc_embed)
            return  
        
        # skip
        if voice_client.is_playing():
            voice_client.stop()
            
            embed = discord.Embed(
                title=f"Skipped!",
                color=self.bot.succesColor
            )
            await context.send(embed=embed)

        else:
            await context.send(embed=self.not_playing_embed)



    @commands.hybrid_command(name="stop", description="Stop the listening session (this clears the queue!)")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def stop(self, context: Context):

        # check dat bot in vc zit
        voice_client = context.message.guild.voice_client
        if voice_client is None:
            await context.send(embed=self.bot_not_in_vc_embed)
            return  
        
        
        if voice_client.is_playing():
            # maak queue leeg
            self.queue = []
            voice_client.stop()
            embed = discord.Embed(
                title=f"Stopped!",
                color=self.bot.defaultColor
            )
            await context.send(embed=embed)

        else:
            await context.send(embed=self.not_playing_embed)

        self.track_playing = None
        self.track_playing_url = None



    @commands.hybrid_command(name="join", description="bot joins voice channel")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def join(self, context: Context):
        try:
            # user zit niet in vc
            if not context.message.author.voice:
                embed = self.not_in_vc_embed
            else:
                # join channel
                channel = context.author.voice.channel
                await channel.connect()
                embed = discord.Embed(
                    title=f"Joined channel {channel.name}!",
                    color=self.bot.succesColor
                )
        except discord.ClientException:
            embed = discord.Embed(
                title=f"Already in voice channel",
                color=self.bot.errorColor
            )
            
        await context.send(embed=embed)
    
        

    @commands.hybrid_command(name="leave", description="bot leaves voice channel")
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def leave(self, context: Context):

        vc = context.message.guild.voice_client
        if vc.is_connected():
            await vc.disconnect()
            embed = discord.Embed(
                title=f"left channel!",
                color=self.bot.succesColor
            )
            await context.send(embed=embed)

        else:
            await context.send(embed=self.not_in_vc_embed)



    async def play_next(self, context: Context):
        vc = context.message.guild.voice_client

        # doe niks zolang player aan het spelen is
        while vc.is_playing():
            await asyncio.sleep(1)

        if len(self.queue) == 0: return

        # krijg volgende url
        url = self.queue.pop(0)
        yt = YouTube(url)
        # video mag max 15 min duren
        try:
            if yt.length > 900:
                embed = discord.Embed(
                    title=f"Video must be less than 15 minutes long.",
                    color=self.bot.errorColor
                ) 
                await context.interaction.followup.send(embed=embed)
                await self.play_next(context)
                return
        except Exception as e:
            self.bot.logger.warning(e)
            pass
        
        # maak temp file aan via url
        filename = await ytdl_helper.YTDLSource.from_url(url, loop=self.bot.loop, ytdl=self.ytdl, bot=self.bot)
        if filename is None:
            embed = discord.Embed(
                title=f"Er is iets misgegaan",
                description=f"ben je zeker dat dit een geldige url is?\n{url}",
                color=self.bot.errorColor
            )
            await context.interaction.followup.send(embed=embed)
            await self.play_next(context)
        else:
            # speel de temp file af
            vc.play(discord.FFmpegPCMAudio(source=filename), after = lambda e: asyncio.run_coroutine_threadsafe(self.play_next(context), self.bot.loop))

            self.track_playing = f"{yt.title} by {yt.author}"
            self.track_playing_url = url

            # confirmatie
            embed = discord.Embed(
                title=f"Playing music!",
                description=f"[{yt.title}]({url}) by {yt.author}",
                color=self.bot.succesColor
            )
            await context.interaction.followup.send(embed=embed)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Audio(bot))
