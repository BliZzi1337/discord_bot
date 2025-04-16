import discord
from discord import app_commands
from discord.ext import commands

FAKTOR = {
    "Byte": 1,
    "Kilobyte": 1000,
    "Megabyte": 1000**2,
    "Gigabyte": 1000**3,
    "Terabyte": 1000**4,
    "Kibibyte": 1024,
    "Mebibyte": 1024**2,
    "Gibibyte": 1024**3,
    "Tebibyte": 1024**4
}

EINHEITEN = [app_commands.Choice(name=k, value=k) for k in FAKTOR.keys()]

def potenz_darstellung(faktor: int) -> str:
    for base in [1000, 1024]:
        for exp in range(1, 6):
            if base ** exp == faktor:
                return f"{base}^{exp}"
    return str(faktor)

class BytesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bytes", description="Rechne Speichergrößen um")
    @app_commands.describe(wert="Wert", von="Von Einheit", zu="Zu Einheit")
    @app_commands.choices(von=EINHEITEN, zu=EINHEITEN)
    async def bytes(self, interaction: discord.Interaction, wert: float, von: app_commands.Choice[str], zu: app_commands.Choice[str]):
        faktor_von = FAKTOR[von.value]
        faktor_zu = FAKTOR[zu.value]
        in_bytes = wert * faktor_von
        ergebnis = in_bytes / faktor_zu

        embed = discord.Embed(
            title="📐 Byte-Umrechnung",
            color=discord.Color.blue()
        )

        embed.add_field(name="🔢 Eingabe", value=f"`{wert} {von.value}`\n= `{in_bytes:,.0f} Bytes`", inline=False)

        embed.add_field(
            name="🔁 Umrechnungsschritte",
            value=(
                f"• 1 {von.value} = {potenz_darstellung(faktor_von)} Bytes\n"
                f"• 1 {zu.value} = {potenz_darstellung(faktor_zu)} Bytes\n"
                f"• {in_bytes:,.0f} ÷ {faktor_zu:,} = **{ergebnis:.6f} {zu.value}**"
            ),
            inline=False
        )

        embed.add_field(name="✅ Ergebnis", value=f"**{wert} {von.value} = {ergebnis:.6f} {zu.value}**", inline=False)

        embed.add_field(
            name="📘 Warum 1000 oder 1024?",
            value=(
                "**Dezimal (SI)**-Einheiten wie *Kilobyte* basieren auf **1000**: z.B. 1 KB = 1000 Bytes.\n"
                "**Binäre (IEC)**-Einheiten wie *Kibibyte* basieren auf **1024 = 2¹⁰**: z.B. 1 KiB = 1024 Bytes.\n\n"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BytesCog(bot))
