
import subprocess
from discord.ext import commands
import os
from discord import app_commands
from math import ceil
import discord
import asyncio
import tempfile
from helpers import checks, http, sptoyt, ytdl_helper
import yt_dlp as youtube_dl
from pytube import Playlist, YouTube, extract
from strprogressbar import ProgressBar
from datetime import datetime



# Here we name the cog and create a new class for the cog.
class Audio(commands.Cog, name="audio"):
    def __init__(self, bot):
        self.bot = bot

        self.bot_not_in_vc_embed = discord.Embed(
            title=f"🔇 Bot is not in vc",
            description="use /join to add bot to vc",
            color=self.bot.errorColor
        ) 

        self.not_playing_embed = discord.Embed(
            title=f"🔇 The bot is not playing anything at the moment.",
            description="Use /play to play a song or playlist",
            color=self.bot.defaultColor
        )

        self.not_in_vc_embed = discord.Embed(
            title=f"🔇 You are not in a voice channel",
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

        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

        self.queue = []
        self.looping = False

        self.pause_time = None
        self.pause_delta = None


    @app_commands.command(name="soundboard", description="Play effect from soundboard (5🪙)", extras={'cog': 'audio'})
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
    @checks.not_in_dm()
    @checks.cost_nword(5)
    @app_commands.describe(effect="Which effect to play")
    async def soundboard(self, interaction, effect: discord.app_commands.Choice[str]):
        """ Play a soundboard effect in vc

        Args:
            interaction (Interaction): Users interaction
            effect (discord.app_commands.Choice[str]): Which effect to play
        """
        # check als user in vc zit
        if not interaction.user.voice:
            await interaction.response.send_message(embed=self.not_in_vc_embed)
            return
        try:

            # check als bot in vc zit
            vc = interaction.guild.voice_client
            if vc is None:
                await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
                return

            # pauzeer reeds spelende audio
            if vc.is_playing():
                vc.pause()

            # speel soundboard af
            vc.play(discord.FFmpegPCMAudio(f"{os.path.realpath(os.path.dirname(__file__))}/../audio_snippets/{effect.value}"), 
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop)
            )
            
            # resume de vorige spelende audio
            if vc.is_paused():
                vc.resume()
            
            # confirmatie 
            embed = discord.Embed(
                title=f"📻 played {effect.name}!",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # error
        except Exception as e:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=e,
                color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)



    @app_commands.command(name="tts", description="Text to Speech (5🪙)", extras={'cog': 'audio'})
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
    @checks.not_in_dm()
    @app_commands.checks.cooldown(rate=1, per=120)
    @checks.cost_nword(5)
    @app_commands.describe(speech="What to say")
    @app_commands.describe(voice="Which voice to say your text in")
    async def tts(self, interaction, speech: str, voice: discord.app_commands.Choice[str]):
        """ Play a tts message in vc

        Args:
            interaction (Interaction): User Interaction
            speech (str): What to say
            voice (discord.app_commands.Choice[str]): Which voice
        """
        # check als user in vc zit
        if not interaction.user.voice:
            await interaction.response.send_message(embed=self.not_in_vc_embed)
            return
        
        # check als bot in vc zit
        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return      
            

        await interaction.response.defer()

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

                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop))
                
                while vc.is_playing():
                    await asyncio.sleep(0.5)
                    
                if vc.is_paused():
                    vc.resume()
            
            # confirmatie
            embed = discord.Embed(
                title=f"🎤 Said ```{speech}``` in a {voice.name} voice!",
                color=self.bot.succesColor
            )
            await interaction.followup.send(embed=embed)


        except Exception as e:
            embed = discord.Embed(
                title=f"Error",
                description=e,
                color=self.bot.errorColor
            )
            await interaction.followup.send(embed=embed)



    @app_commands.command(name="play", description="play a youtube video or playlist (use multiple times to add to queue)", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    @app_commands.choices(in_front=[
        discord.app_commands.Choice(name="no", value=0),
        discord.app_commands.Choice(name="yes", value=1),   
    ])
    @app_commands.describe(url="The url of the video or playlist you want to play (Youtube or Spotify)")
    @app_commands.describe(in_front="Whether the track should be in the front of the queue or in the back")
    async def play(self, interaction, url: str, in_front: discord.app_commands.Choice[int]=0):
        """ Play audio from a video

        Args:
            interaction (Interaction): User Interaction
            url (str): url of youtube video/playlist or spotify playlist/song
            in_front (discord.app_commands.Choice[int]): If the audio has to be played now or put in queue
        """


        # check dat user in vc zit
        if not interaction.user.voice:
            await interaction.response.send_message(embed=self.not_in_vc_embed)
            return
        
        # check dat bot in vc zit
        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return  
        
        await interaction.response.defer()

        # in_front kan value hebben als param door user gesubmit is, anders is het al int
        try:
            in_front = in_front.value
        except:
            pass
        
        try:

            # youtube playlist
            if url.find("list=") != -1 or url.find("open.spotify.com/playlist") != -1:

                    # krijg afzonderlijke urls van videos in playlist 
                    # voeg de urls toe aan queue
                    desc = ""
                    if url.find("list=") != -1:
                        vid_urls = Playlist(url)
                    else:
                        spToYt = sptoyt.SpotifyToYT()
                        vid_urls = spToYt.spotifyToYoutubeURLs(url)


                    for i, vid_url in enumerate(vid_urls):
                        if in_front == 1:
                            self.queue.insert(0, vid_url)
                        else:
                            self.queue.append(vid_url)
                        yt = YouTube(vid_url)

                        if i<10:
                            desc += f"{i+1}: [{yt.title}]({vid_url}) by {yt.author}\n\n"

                    embed = discord.Embed(
                        title=f"🎶 Added to Queue!",
                        description=desc,
                        color=self.bot.succesColor
                    )
                    await interaction.followup.send(embed=embed)
                    
                    if not vc.is_playing():
                        await self.play_next(interaction)
                        return

            # enkele video
            else:
                # check als url spotify track is of yt vid
                if url.find("open.spotify.com/track") != -1:
                    spToYt = sptoyt.SpotifyToYT()
                    url = spToYt.spotifyToYoutubeURLs(url)
                
                yt = YouTube(url)
                
                # voeg lied aan queue toe
                if in_front == 1:
                    self.queue.insert(0, url)
                else:
                    self.queue.append(url)
                
                # stuur confirmatie dat lied is toegevoegd
                if vc.is_playing():
                    
                    embed = discord.Embed(
                        title=f"🎵 Added to Queue",
                        description=f"[{yt.title}]({url}) by {yt.author}",
                        color=self.bot.defaultColor
                    )

                    try:
                        vid_id = extract.video_id(url)
                        embed.set_thumbnail(
                            url=f"http://img.youtube.com/vi/{vid_id}/0.jpg"
                        )
                    except:
                        pass


                    await interaction.followup.send(embed=embed)
                    return

                await self.play_next(interaction, True)
            

        except Exception as e:
            self.bot.logger.error(e)
            embed = discord.Embed(
                title=f"Er is iets misgegaan",
                description=f"ben je zeker dat dit een geldige url is?\n{url}\n{e}",
                color=self.bot.errorColor
            )
            await interaction.followup.send(embed=embed)
            return



    @app_commands.command(name="list", description="See the Queue", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def list(self, interaction):
        """List the videos in queue

        Args:
            interaction (Interaction): Users Interaction
        """

        # lege queue
        if len(self.queue) == 0:
            embed = discord.Embed(
                title=f"📝 Queue is empty!",
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
                title=f"📝 Queue",
                description=desc,
                color=self.bot.defaultColor
            )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="nowplaying", description="See the currently playing track", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def nowplaying(self, interaction):
        """Which audio is now playing

        Args:
            interaction (Interaction): Users interaction
        """

        try:
            title="🎵 Now playing" if self.track_playing is not None else "❌ Nothing is playing"
            desc = f"[{self.track_playing}]({self.track_playing_url})" if self.track_playing is not None else None
        except:
            title="❌ Nothing is playing"
            desc = None

        embed = discord.Embed(
            title=title,
            description=desc,
            color=self.bot.defaultColor
        )

        try:
            vid_id = extract.video_id(self.track_playing_url)
            embed.set_thumbnail(
                url=f"http://img.youtube.com/vi/{vid_id}/0.jpg"
            )
        except:
            pass

        await interaction.response.send_message(embed=embed)
      


    @app_commands.command(name="pause", description="Pause currently playing track", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def pause(self, interaction):
        """ Pauses the playing audio

        Args:
            interaction (Interaction): Users Interaction
        """

        # check als bot in vc zit
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return  
        
        # pauzeer
        if voice_client.is_playing():
            voice_client.pause()
            self.pause_time = datetime.now()
            embed = discord.Embed(
                title=f"⏸️ Paused!",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=self.not_playing_embed)
      
        

    @app_commands.command(name="resume", description="Resume currently playing track", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def resume(self, interaction):
        """Resumes the paused audio

        Args:
            interaction (Interaction): Users Interaction
        """

        # check als bot in vc zit
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return  
        
        # resume
        if voice_client.is_paused():
            # calculate pause delta
            if not self.pause_delta:
                self.pause_delta = datetime.now() - self.pause_time
            else:
                self.pause_delta += datetime.now() - self.pause_time
            
            self.pause_time = None

            voice_client.resume()
            embed = discord.Embed(
                title=f"▶️ Resumed!",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=self.not_playing_embed)


    @app_commands.command(name="loop", description="Loop the queue", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def loop(self, interaction):
        """ Loop the queue

        Args:
            interaction (Interaction): Users Interaction
        """

        # check als bot in vc zit
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return  
        
        if voice_client.is_playing():

            # currently playing track should also be included in the loop
            if (self.queue or [None])[-1] != self.track_playing_url:
                self.queue.append(self.track_playing_url)

            # turn looping on/off
            self.looping = not self.looping

            embed = discord.Embed(
                title="🔁 Looping enabled!" if self.looping else "🔁 Looping disabled!",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=self.not_playing_embed)



    @app_commands.command(name="skip", description="Skip the currently playing track", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    @app_commands.describe(aantal="How many tracks the bot should skip")
    async def skip(self, interaction, aantal:int=1):
        """Skips the currently playing audio

        Args:
            interaction (Interaction): Users Interaction
            aantal (int): amount of tracks to skip, defaults to 1
        """

        # check als bot in vc zit
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return  
        
        # skip
        if voice_client.is_playing():
            self.queue = self.queue[aantal-1:]
            voice_client.stop()

            # tijdstippen hebben we niet meer nodig
            self.pause_time = None
            self.pause_delta = None
            
            embed = discord.Embed(
                title=f"⏭️ Skipped!",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_message(embed=self.not_playing_embed)



    @app_commands.command(name="stop", description="Stop the listening session (this clears the queue!)", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def stop(self, interaction):
        """ Stops the listening session & clears the queue

        Args:
            interaction (Interaction): Users Interaction
        """

        # check dat bot in vc zit
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message(embed=self.bot_not_in_vc_embed)
            return  
        
        
        if voice_client.is_playing():
            # maak queue leeg
            self.queue = []
            # tijdstippen hebben we niet meer nodig
            self.pause_time = None
            self.pause_delta = None
            
            voice_client.stop()
            embed = discord.Embed(
                title=f"⏹️ Stopped!",
                color=self.bot.defaultColor
            )
            await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_message(embed=self.not_playing_embed)

        self.track_playing = None
        self.track_playing_url = None



    @app_commands.command(name="join", description="bot joins voice channel", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def join(self, interaction):
        """Joins a vc

        Args:
            interaction (Interaction): Users Interaction
        """

        try:
            # user zit niet in vc
            if not interaction.user.voice:
                embed = self.not_in_vc_embed
            else:
                # join channel
                channel = interaction.user.voice.channel
                await channel.connect()
                embed = discord.Embed(
                    title=f"✅ Joined channel {channel.name}!",
                    color=self.bot.succesColor
                )
        except discord.ClientException:
            embed = discord.Embed(
                title=f"🎧 Already in voice channel",
                color=self.bot.errorColor
            )
            
        await interaction.response.send_message(embed=embed)
    
        

    @app_commands.command(name="leave", description="bot leaves voice channel", extras={'cog': 'audio'})
    @checks.not_blacklisted()
    @checks.in_audio_command_channel()
    @checks.not_in_dm()
    async def leave(self, interaction):
        """leaves a vc

        Args:
            interaction (Interaction): Users Interaction
        """

        vc = interaction.guild.voice_client
        if vc.is_connected():
            await vc.disconnect()
            embed = discord.Embed(
                title=f"🤖 left channel!",
                color=self.bot.succesColor
            )
            await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_message(embed=self.not_in_vc_embed)



    async def play_next(self, interaction, first_player=False):
        """Plays the next audio in queue

        Args:
            interaction (Interaction): Users interaction
        """
        vc = interaction.guild.voice_client

        # doe niks zolang player aan het spelen is
        
        if len(self.queue) == 0: return

        # krijg volgende url
        url = self.queue.pop(0)

        # voeg url terug toe aan queue als loop aanstaat
        if self.looping:
            self.queue.append(url)

        yt = YouTube(url)
        # video mag max 15 min duren
        try:
            if yt.length > 900:
                embed = discord.Embed(
                    title=f"Video must be less than 15 minutes long.",
                    color=self.bot.errorColor
                )
                if first_player:
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.channel.send(embed=embed)
                await self.play_next(interaction)
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
            if first_player:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.channel.send(embed=embed)
            await self.play_next(interaction)

        else:
            # speel de temp file af
            vc.play(discord.FFmpegPCMAudio(source=filename), after = lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop))

            self.track_playing = f"{yt.title} by {yt.author}"
            self.track_playing_url = url

            # creeer een progress bar
            total = 20
            current = 0
            # First two arguments are mandatory
            bardata = ProgressBar(current, total, 18)

            # confirmatie
            embed = discord.Embed(
                title=f"🎵 Playing music!",
                description=f"[{yt.title}]({url}) by {yt.author}\n{bardata} - {self.format_seconds_to_mmss(0)} / {self.format_seconds_to_mmss(yt.length)}",
                color=self.bot.succesColor
            )

            try:
                vid_id = extract.video_id(self.track_playing_url)
                embed.set_thumbnail(
                    url=f"http://img.youtube.com/vi/{vid_id}/0.jpg"
                )
            except:
                pass


            if first_player:
                playing_message = await interaction.followup.send(embed=embed)
            else:
                playing_message = await interaction.channel.send(embed=embed)

            total = yt.length
            start_time = datetime.now()
            time_delay = float(os.environ.get("time_delay"))
            while vc.is_playing() or vc.is_paused():
                if vc.is_paused():
                    embed.description = "⏸️ **Paused!**\n" + embed.description.replace('⏸️ **Paused!**\n', '')
                else:
                    # creeer een progress bar
                    # bereken time diff
                    if self.pause_delta:
                        time_diff = datetime.now() - start_time - self.pause_delta
                    else:
                        time_diff = datetime.now() - start_time

                    bardata = ProgressBar(ceil(time_diff.total_seconds()), total, 18)
                    first_desc = embed.description.replace('⏸️ **Paused!**\n', '').split('\n')[0]
                    embed.description = f"{first_desc}\n{bardata} - {self.format_seconds_to_mmss(time_diff.seconds)} / {self.format_seconds_to_mmss(yt.length)}"
                
                try:
                    await playing_message.edit(embed=embed)

                except Exception as e:
                    self.bot.logger.warning(e)

                # hoeveel keer de progress bar w geupdate
                await asyncio.sleep(time_delay)

            # ten laatste zetten we de progress bar op de laatste seconde
            bardata = ProgressBar(total, total, 18)
            first_desc = embed.description.split('\n')[0].replace('⏸️ **Paused!**', '')
            formatted_length = self.format_seconds_to_mmss(yt.length)
            embed.description = f"{first_desc}\n{bardata} - {formatted_length} / {formatted_length}"
            await playing_message.edit(embed=embed)

            # tijdstippen hebben we niet meer nodig
            self.pause_time = None
            self.pause_delta = None


    def format_seconds_to_mmss(self, seconds):
        minutes = seconds // 60
        seconds %= 60
        return "%02i:%02i" % (minutes, seconds)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Audio(bot))
