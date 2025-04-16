
import discord
from discord.ext import commands, tasks
import datetime
import pytz
import os

GUILD_ID = 1335923619242577971  # DAA Server
VOICE_FROM = int(os.getenv("VOICE_FROM"))
VOICE_TO_PREFIX = "🔊︱Talk #"
ADMIN_TALK_CHANNEL = 1347112565704101910

class AutoMover(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.move_users.start()

    def cog_unload(self):
        self.move_users.cancel()

    @tasks.loop(minutes=1)
    async def move_users(self):
        now = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
        if now.weekday() in [1, 2, 3, 4] and now.hour == 11 and now.minute == 15:
            await self.perform_move()

    async def perform_move(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        from_channel = guild.get_channel(VOICE_FROM)
        if not from_channel or not from_channel.members:
            return

        # Finde alle Talk Channels und ihre Belegung
        talk_channels = []
        for channel in guild.voice_channels:
            if channel.name.startswith(VOICE_TO_PREFIX):
                talk_channels.append({
                    'channel': channel,
                    'number': int(channel.name.split('#')[-1]),
                    'members': len(channel.members)
                })

        # Sortiere nach Nummer
        talk_channels.sort(key=lambda x: x['number'])

        # Finde den ersten leeren Talk Channel
        target_channel = None
        for channel_info in talk_channels:
            if channel_info['members'] == 0:
                target_channel = channel_info['channel']
                break

        if target_channel:
            # Liste für verschobene Mitglieder
            moved_members = []
            
            # Verschiebe alle Mitglieder
            for member in from_channel.members:
                try:
                    await member.move_to(target_channel)
                    moved_members.append(member.mention)
                except discord.HTTPException:
                    pass
            
            # Erstelle und sende das Embed
            if moved_members:
                embed = discord.Embed(
                    title="🔄 Automatische Verschiebung",
                    description=f"Es ist 11:15 Uhr - Zeit für Talk!",
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="Von", value=from_channel.mention, inline=True)
                embed.add_field(name="Nach", value=target_channel.mention, inline=True)
                embed.add_field(name="Verschobene Mitglieder", value="\n".join(moved_members), inline=False)
                embed.set_footer(text=f"Insgesamt verschoben: {len(moved_members)}")
                
                # Sende das Embed in den Admin Talk Channel
                channel = self.bot.get_channel(ADMIN_TALK_CHANNEL)
                if channel:
                    await channel.send(embed=embed)

    @move_users.before_loop
    async def before_move_users(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AutoMover(bot))
