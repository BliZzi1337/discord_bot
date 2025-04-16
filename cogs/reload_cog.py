import discord
from discord.ext import commands
from discord import app_commands
from cog_loader import list_cogs

OWNER_IDS = [157768440210259968, 388936796387409921]  # Chris, Michael

class ReloadView(discord.ui.View):
    def __init__(self, bot: commands.Bot, cogs: list[str]):
        super().__init__(timeout=60)
        self.add_item(ReloadDropdown(bot, cogs))


class ReloadDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot, cogs: list[str]):
        self.bot = bot
        options = [
            discord.SelectOption(label=cog, description=f"{cog}.py neu laden")
            for cog in cogs
        ]
        super().__init__(placeholder="Wähle Cogs zum Neuladen aus", min_values=1, max_values=len(cogs), options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("❌ Nicht autorisiert", ephemeral=True)
            return

        cog_name = self.values[0]
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            await interaction.response.send_message(f"✅ `{cog_name}` wurde neu geladen.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Fehler beim Reload:\n```{e}```", ephemeral=True)


class ReloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Lade Cog-Module neu (Dropdown-Auswahl)")
    async def reload(self, interaction: discord.Interaction):
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("❌ Nur Owner dürfen reloaden!", ephemeral=True)
            return

        cogs = list_cogs(exclude=["reload_cog"])
        if not cogs:
            await interaction.response.send_message("⚠️ Keine Cogs gefunden.", ephemeral=True)
            return

        view = ReloadView(self.bot, cogs)
        await interaction.response.send_message("🔄 Wähle Cogs zum Neuladen:", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReloadCog(bot))
