import discord
from discord.ext import commands
from discord import Interaction, app_commands
import os
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

# Admin-Rollen-ID und Guild-ID aus der .env-Datei holen
# Mehrere Admin-Rollen-IDs aus der .env laden
ADMIN_ROLE_IDS = [int(role_id.strip()) for role_id in os.getenv("ADMIN_ROLE_IDS", "").split(",")]
GUILD_ID = 1107964583928418324  # DAA Server

class MoveAnywhere(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="verschieben", description="Verschiebe alle Mitglieder aus deinem Kanal in einen anderen Kanal")
    @app_commands.describe(
        nach_channel="In welchen Sprachkanal sollen die Mitglieder verschoben werden?"
    )
    async def verschieben(self, interaction: Interaction, nach_channel: discord.VoiceChannel):
        # Admincheck
        if not any(role.id in ADMIN_ROLE_IDS for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 Du hast keine Berechtigung, diesen Befehl zu verwenden.", ephemeral=True)

        # Hole den aktuellen Kanal des Nutzers
        von_channel = interaction.user.voice.channel

        if not von_channel:
            return await interaction.response.send_message("❌ Du bist in keinem Sprachkanal.", ephemeral=True)

        verschobene = []

        # Verschiebe alle Mitglieder in den angegebenen Kanal
        for member in von_channel.members:
            try:
                await member.move_to(nach_channel)
                verschobene.append(member.mention)
            except discord.HTTPException:
                pass

        # Erstelle Embed für die Antwort
        embed = discord.Embed(title="🔄 Mitglieder wurden verschoben", color=discord.Color.blurple())
        embed.add_field(name="Von", value=f"{von_channel.mention}", inline=True)
        embed.add_field(name="Nach", value=f"{nach_channel.mention}", inline=True)

        # Wenn es verschobene Mitglieder gibt
        if verschobene:
            embed.add_field(name="Verschobene Mitglieder", value="\n".join(verschobene), inline=False)
            embed.set_footer(text=f"Insgesamt verschoben: {len(verschobene)}")
        else:
            embed.description = "Es waren keine Mitglieder im Quellkanal oder alle konnten nicht verschoben werden."

        # Sende die Antwort an den Nutzer
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(MoveAnywhere(bot))