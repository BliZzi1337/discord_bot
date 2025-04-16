
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class WheelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="rad", description="Startet ein Glücksrad und wählt zufällig ein Mitglied aus")
    async def wheel(self, interaction: discord.Interaction):
        # Get the specific server
        guild = self.bot.get_guild(1335923619242577971)
        if not guild:
            return await interaction.response.send_message("❌ Server nicht gefunden!", ephemeral=True)
            
        # Filter members: no bots and exclude specific user
        members = [m for m in guild.members 
                  if not m.bot and m.id != 1028552092304031754]
        
        if len(members) < 2:
            return await interaction.response.send_message("❌ Nicht genug Mitglieder verfügbar!", ephemeral=True)

        # Erstelle das erste Embed
        embed = discord.Embed(title="🎡 Glücksrad", description="Das Rad dreht sich...", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
        
        # Animation (5 Durchgänge)
        for _ in range(5):
            await asyncio.sleep(0.7)
            random_members = random.sample(members, min(3, len(members)))
            embed.clear_fields()
            for member in random_members:
                embed.add_field(name="➡️ Kandidat", value=member.display_name, inline=True)
            await interaction.edit_original_response(embed=embed)
            
        # Wähle Gewinner
        winner = random.choice(members)
        embed.description = f"🎉 Das Rad hat gewählt!\n\n**Gewinner: {winner.mention}**"
        embed.color = discord.Color.green()
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(WheelCog(bot))
