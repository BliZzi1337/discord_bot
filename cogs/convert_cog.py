import discord
from discord import app_commands, Interaction
from discord.ext import commands

basis_map = {
    "Binär": 2,
    "Dezimal": 10,
    "Hexadezimal": 16
}

symbol_map = "0123456789ABCDEF"

# Binär in 4er-Blöcke mit Leerzeichen
def format_bin_with_spaces(bin_str: str) -> str:
    bin_str = bin_str.zfill((len(bin_str) + 3) // 4 * 4)
    return " ".join(bin_str[i:i+4] for i in range(0, len(bin_str), 4))

# Hex in 2er-Blöcke mit Leerzeichen
def format_hex_with_spaces(hex_str: str) -> str:
    hex_str = hex_str.upper()
    if len(hex_str) % 2 != 0:
        hex_str = "0" + hex_str
    return " ".join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))

# Rechenweg: Dezimal zu Binär oder Hex
def dezimal_division_rechenweg(wert: int, basis: int) -> str:
    restliste = []
    temp = wert

    while temp > 0:
        q, r = divmod(temp, basis)
        restliste.append((temp, q, r))
        temp = q

    if basis == 16:
        ergebnis = format_hex_with_spaces(hex(wert)[2:])
    elif basis == 2:
        ergebnis = format_bin_with_spaces(bin(wert)[2:])
    else:
        ergebnis = str(wert)

    schritte = [
        f"{i+1}. {v:<10} ÷ {basis:<2} = {q:<6} Rest {symbol_map[r]}"
        for i, (v, q, r) in enumerate(restliste)
    ]

    return "\n".join(schritte) + "\n" + "─" * 30 + f"\n➡️ Ergebnis: {ergebnis}"

# Rechenweg: Binär/Hex zu Dezimal
def stellenwert_rechenweg(wert: str, basis: int) -> str:
    wert = wert.upper()[::-1]
    ergebnis = 0
    teile = []

    for i, zeichen in enumerate(wert):
        z = symbol_map.index(zeichen)
        potenz = z * (basis ** i)
        teile.append(f"{zeichen}×{basis}^{i} = {potenz}")
        ergebnis += potenz

    teile.reverse()
    return "\n".join(teile) + "\n" + "─" * 30 + f"\n➡️ Ergebnis: {ergebnis}"

# Umwandlungslogik + Rechenweg
def umwandeln_mit_rechenweg(wert: str, von: str, zu: str) -> tuple[str, str, str]:
    try:
        dezimalwert = int(wert, base=basis_map[von])
    except ValueError:
        return "Fehler", f"⚠️ Ungültiger {von}-Wert: `{wert}`", ""

    if zu == "Binär":
        zielwert = bin(dezimalwert)[2:]
        zielwert = format_bin_with_spaces(zielwert)
    elif zu == "Hexadezimal":
        zielwert = format_hex_with_spaces(hex(dezimalwert)[2:])
    elif zu == "Dezimal":
        zielwert = str(dezimalwert)
    else:
        return "Fehler", f"⚠️ Unbekanntes Zielsystem: `{zu}`", ""

    if von == "Dezimal":
        rechenweg = dezimal_division_rechenweg(int(wert), basis_map[zu])
    elif zu == "Dezimal":
        rechenweg = stellenwert_rechenweg(wert, basis_map[von])
    else:
        erste = stellenwert_rechenweg(wert, basis_map[von])
        zweite = dezimal_division_rechenweg(dezimalwert, basis_map[zu])
        rechenweg = f"{erste}\n\n➡️ Zwischenergebnis: {dezimalwert} (Dezimal)\n\n{zweite}"

    return zielwert, f"{wert} ({von}) = {zielwert} ({zu})", rechenweg

# Cog
class ConvertCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="convert", description="Zahlensysteme umrechnen (mit Rechenweg)")
    @app_commands.describe(
        wert="Zahl, die du umwandeln willst",
        von="Ausgangsbasis",
        zu="Zielbasis"
    )
    @app_commands.choices(
        von=[
            app_commands.Choice(name="Binär", value="Binär"),
            app_commands.Choice(name="Dezimal", value="Dezimal"),
            app_commands.Choice(name="Hexadezimal", value="Hexadezimal")
        ],
        zu=[
            app_commands.Choice(name="Binär", value="Binär"),
            app_commands.Choice(name="Dezimal", value="Dezimal"),
            app_commands.Choice(name="Hexadezimal", value="Hexadezimal")
        ]
    )
    async def convert(
        self,
        interaction: Interaction,
        wert: str,
        von: app_commands.Choice[str],
        zu: app_commands.Choice[str]
    ):
        zielwert, info, rechenweg = umwandeln_mit_rechenweg(wert, von.value, zu.value)
        embed = discord.Embed(title="🔄 Zahlenumwandlung", color=0x3bff8f)

        if zielwert == "Fehler":
            embed.description = info
        else:
            if von.value == "Binär":
                anzeige_wert = format_bin_with_spaces(wert)
            elif von.value == "Hexadezimal":
                anzeige_wert = format_hex_with_spaces(wert)
            else:
                anzeige_wert = wert

            embed.add_field(name="Eingabe", value=f"```{anzeige_wert} ({von.value})```", inline=True)
            embed.add_field(name="Ergebnis", value=f"```{zielwert} ({zu.value})```", inline=True)

            if rechenweg:
                embed.add_field(name="🧠 Rechenweg", value=f"```{rechenweg}```", inline=False)

            embed.set_footer(
                text=f"Berechnung von {von.value} in {zu.value}",
                icon_url="https://images.vexels.com/media/users/3/254864/isolated/preview/0d66d80f601ab3bf21b9d65caf289c96-schule-klassenzimmericons-youngsweet-vinylcolor-cr-11.png"
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

# Setup
async def setup(bot: commands.Bot):
    await bot.add_cog(ConvertCog(bot))
