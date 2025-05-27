import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# تكوين الخيارات الخاصة بتحميل الفيديو
YTDL_OPTIONS = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

# تكوين خيارات FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# إنشاء مجلد للتحميلات إذا لم يكن موجوداً
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# إنشاء مثيل من YoutubeDL
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        self.current_song = None
        self.ytdl = ytdl

    async def setup_hook(self):
        await self.add_commands()
        await self.tree.sync()
        print(f'{self.user} تم تشغيل البوت بنجاح!')

    async def get_audio_source(self, url):
        """الحصول على مصدر الصوت من الرابط"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            
            if 'entries' in data:
                data = data['entries'][0]
            
            return {
                'url': data.get('url'),
                'title': data.get('title'),
                'duration': data.get('duration')
            }
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None

    async def add_commands(self):
        @self.tree.command(name="play", description="تشغيل مقطع صوتي من يوتيوب")
        async def play(interaction: discord.Interaction, url: str):
            if not interaction.user.voice:
                await interaction.response.send_message("يجب أن تكون في قناة صوتية!", ephemeral=True)
                return

            voice_channel = interaction.user.voice.channel
            voice_client = interaction.guild.voice_client

            await interaction.response.defer()

            try:
                if voice_client is None:
                    voice_client = await voice_channel.connect()
                elif voice_client.channel != voice_channel:
                    await voice_client.move_to(voice_channel)

                audio_info = await self.get_audio_source(url)
                if not audio_info:
                    await interaction.followup.send("❌ لم أتمكن من العثور على المقطع الصوتي", ephemeral=True)
                    return

                if voice_client.is_playing():
                    voice_client.stop()

                try:
                    source = await discord.FFmpegOpusAudio.from_probe(
                        audio_info['url'],
                        method='fallback',
                        **FFMPEG_OPTIONS
                    )
                    
                    def after_playing(error):
                        if error:
                            print(f"Error after playing: {error}")
                            asyncio.run_coroutine_threadsafe(
                                interaction.channel.send("❌ حدث خطأ أثناء التشغيل"),
                                asyncio.get_event_loop()
                            )
                        else:
                            asyncio.run_coroutine_threadsafe(
                                interaction.channel.send("✅ انتهى تشغيل المقطع الصوتي"),
                                asyncio.get_event_loop()
                            )

                    voice_client.play(source, after=after_playing)
                    self.current_song = audio_info['title']
                    
                    duration = audio_info.get('duration')
                    duration_text = f" (المدة: {duration//60}:{duration%60:02d})" if duration else ""
                    
                    await interaction.followup.send(f'🎵 جاري تشغيل: {audio_info["title"]}{duration_text}')

                except Exception as e:
                    print(f"Error playing audio: {e}")
                    await interaction.followup.send(f"حدث خطأ أثناء محاولة تشغيل الصوت: {str(e)}", ephemeral=True)

            except Exception as e:
                print(f"Error in play command: {e}")
                await interaction.followup.send(f'حدث خطأ: {str(e)}', ephemeral=True)

        @self.tree.command(name="stop", description="إيقاف تشغيل الموسيقى والخروج من القناة")
        async def stop(interaction: discord.Interaction):
            voice_client = interaction.guild.voice_client
            if voice_client:
                voice_client.stop()
                await voice_client.disconnect()
                self.current_song = None
                await interaction.response.send_message("تم إيقاف التشغيل ✋")
            else:
                await interaction.response.send_message("البوت غير متصل بأي قناة صوتية!", ephemeral=True)

        @self.tree.command(name="pause", description="إيقاف الموسيقى مؤقتاً")
        async def pause(interaction: discord.Interaction):
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                voice_client.pause()
                await interaction.response.send_message("تم إيقاف التشغيل مؤقتاً ⏸️")
            else:
                await interaction.response.send_message("لا يوجد شيء قيد التشغيل!", ephemeral=True)

        @self.tree.command(name="resume", description="استئناف تشغيل الموسيقى")
        async def resume(interaction: discord.Interaction):
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_paused():
                voice_client.resume()
                await interaction.response.send_message("تم استئناف التشغيل ▶️")
            else:
                await interaction.response.send_message("لا يوجد شيء متوقف مؤقتاً!", ephemeral=True)

        @self.tree.command(name="nowplaying", description="عرض المقطع الصوتي الحالي")
        async def nowplaying(interaction: discord.Interaction):
            if self.current_song:
                await interaction.response.send_message(f"🎵 يتم الآن تشغيل: {self.current_song}")
            else:
                await interaction.response.send_message("لا يوجد شيء قيد التشغيل!", ephemeral=True)

# تشغيل البوت
def main():
    bot = MusicBot()
    # الحصول على التوكن من المتغيرات البيئية
    token = os.getenv('MTM3NzAyNjA1MjE4MTg1MjMzNA.GPo-OO.RarKydvUYGe3I8N9UERVv3aNGLBCbae8Uo6ENU')
    if not token:
        raise ValueError("لم يتم العثور على توكن البوت! تأكد من وجود ملف .env")
    bot.run(token)

if __name__ == "__main__":
    main() 
