import math
import traceback
import discord
from discord.ext import commands
from discord import Interaction, app_commands

ZIEL_MAPPING = {
    "Kapazität": "Kapazität",
    "Leistung": "Leistung",
    "Zeit": "Zeit",
    "Spannung": "Spannung",
    "Akkus": "Akkus",
    "Watt → VA": "Watt → VA",
    "VA → Watt": "VA → Watt"
}

class USVInputModal(discord.ui.Modal):
    def __init__(self, ziel: str):
        super().__init__(title="USV Eingabemaske")
        self.ziel = ziel

        if ziel == "Watt → VA":
            self.add_item(discord.ui.TextInput(label="Leistung (W)", placeholder="z. B. 300", required=True))
        elif ziel == "VA → Watt":
            self.add_item(discord.ui.TextInput(label="Scheinleistung (VA)", placeholder="z. B. 465", required=True))
        else:
            if ziel != "Kapazität":
                self.add_item(discord.ui.TextInput(label="Kapazität (Ah)", placeholder="z. B. 7.2", required=True))
            if ziel != "Leistung":
                self.add_item(discord.ui.TextInput(label="Leistung (W)", placeholder="z. B. 300", required=True))
            if ziel != "Zeit":
                self.add_item(discord.ui.TextInput(label="Zeit (min)", placeholder="z. B. 15", required=True))
            if ziel != "Spannung":
                self.add_item(discord.ui.TextInput(label="Spannung (V)", placeholder="z. B. 12 oder 24", required=True))
            if ziel != "Akkus":
                self.add_item(discord.ui.TextInput(label="Wirkungsgrad (%)", required=False, placeholder="leer lassen = 100%"))
            if ziel == "Akkus":
                self.add_item(discord.ui.TextInput(label="Kapazität pro Akku (Ah)", placeholder="z. B. 7.2", required=True))

    async def on_submit(self, interaction: Interaction):
        try:
            print(f"🧪 Modal geöffnet mit Ziel: {self.ziel} von {interaction.user.display_name}")

            felder = {
                i.label.split()[0].lower(): float(i.value.replace(",", "."))
                for i in self.children if isinstance(i, discord.ui.TextInput) and i.value and "Wirkungsgrad" not in i.label and "Akku" not in i.label
            }

            wirkungsgrad_text = next((i.value for i in self.children if "Wirkungsgrad" in i.label), "")
            wirkungsgrad = float(wirkungsgrad_text.replace(",", ".")) if wirkungsgrad_text else 100.0
            wirkungsgrad_faktor = wirkungsgrad / 100

            einzelakku_text = next((i.value for i in self.children if "Kapazität pro Akku" in i.label), "")
            einzelakku = float(einzelakku_text.replace(",", ".")) if einzelakku_text else None

            embed = discord.Embed(title=f"🔧 USV-Rechnung – {self.ziel}", color=discord.Color.orange())

            eingabe_text = "\n".join([f"• {k.capitalize()}: {v}" for k, v in felder.items()])
            if wirkungsgrad_text:
                eingabe_text += f"\n• Wirkungsgrad: {wirkungsgrad:.2f} %"
            if einzelakku:
                eingabe_text += f"\n• Kapazität pro Akku: {einzelakku} Ah"
            embed.add_field(name="📥 Eingabe", value=eingabe_text, inline=False)

            match self.ziel:
                case "Watt → VA":
                    watt = felder["leistung"]
                    va = watt * 1.55
                    ergebnis = va
                    rechenweg = f"1. VA = {watt:.2f} W × 1.55 = **{va:.2f} VA**"

                case "VA → Watt":
                    va = felder["scheinleistung"]
                    watt = va * 0.65
                    ergebnis = watt
                    rechenweg = f"1. Watt = {va:.2f} VA × 0.65 = **{watt:.2f} W**"

                case "Kapazität":
                    watt = felder["leistung"]
                    zeit = felder["zeit"] / 60
                    spannung = felder["spannung"]
                    energiebedarf = watt * zeit
                    effektiv = energiebedarf / wirkungsgrad_faktor
                    ergebnis = effektiv / spannung
                    rechenweg = (
                        f"1. Energiebedarf = {watt:.2f} W × {zeit:.2f} h = {energiebedarf:.2f} Wh\n"
                        f"2. Effektiv = {energiebedarf:.2f} Wh ÷ {wirkungsgrad_faktor:.2f} = {effektiv:.2f} Wh\n"
                        f"3. Kapazität = {effektiv:.2f} Wh ÷ {spannung:.2f} V = **{ergebnis:.2f} Ah**"
                    )

                case "Leistung":
                    ah = felder["kapazität"]
                    spannung = felder["spannung"]
                    zeit = felder["zeit"] / 60
                    watt = (ah * spannung * wirkungsgrad_faktor) / zeit
                    ergebnis = watt
                    rechenweg = (
                        f"1. Energie = {ah:.2f} Ah × {spannung:.2f} V = {ah * spannung:.2f} Wh\n"
                        f"2. Nutzbar = {ah * spannung:.2f} Wh × {wirkungsgrad_faktor:.2f} = {(ah * spannung * wirkungsgrad_faktor):.2f} Wh\n"
                        f"3. Leistung = {(ah * spannung * wirkungsgrad_faktor):.2f} Wh ÷ {zeit:.2f} h = **{ergebnis:.2f} W**"
                    )

                case "Zeit":
                    ah = felder["kapazität"]
                    spannung = felder["spannung"]
                    watt = felder["leistung"]
                    nutzbar = ah * spannung * wirkungsgrad_faktor
                    zeit = nutzbar / watt * 60
                    ergebnis = zeit
                    rechenweg = (
                        f"1. Energie = {ah:.2f} Ah × {spannung:.2f} V = {ah * spannung:.2f} Wh\n"
                        f"2. Nutzbar = {ah * spannung:.2f} Wh × {wirkungsgrad_faktor:.2f} = {nutzbar:.2f} Wh\n"
                        f"3. Zeit = {nutzbar:.2f} Wh ÷ {watt:.2f} W × 60 = **{zeit:.2f} Minuten**"
                    )

                case "Spannung":
                    watt = felder["leistung"]
                    zeit = felder["zeit"] / 60
                    ah = felder["kapazität"]
                    energiebedarf = watt * zeit
                    effektiv = energiebedarf / wirkungsgrad_faktor
                    spannung = effektiv / ah
                    ergebnis = spannung
                    rechenweg = (
                        f"1. Energiebedarf = {watt:.2f} W × {zeit:.2f} h = {energiebedarf:.2f} Wh\n"
                        f"2. Effektiv = {energiebedarf:.2f} Wh ÷ {wirkungsgrad_faktor:.2f} = {effektiv:.2f} Wh\n"
                        f"3. Spannung = {effektiv:.2f} Wh ÷ {ah:.2f} Ah = **{spannung:.2f} V**"
                    )

                case "Akkus":
                    watt = felder.get("leistung")
                    zeit = felder.get("zeit") / 60
                    spannung = felder.get("spannung")
                    if not einzelakku:
                        raise ValueError("⚠️ Kapazität pro Akku fehlt oder ist ungültig.")
                    energiebedarf = watt * zeit
                    effektiv = energiebedarf / wirkungsgrad_faktor
                    gesamtkapazitaet = effektiv / spannung
                    akkus = gesamtkapazitaet / einzelakku
                    aufgerundet = math.ceil(akkus)
                    ergebnis = aufgerundet
                    rechenweg = (
                        f"1. Energiebedarf = {watt:.2f} W × {zeit:.2f} h = {energiebedarf:.2f} Wh\n"
                        f"2. Effektiv = {energiebedarf:.2f} Wh ÷ {wirkungsgrad_faktor:.2f} = {effektiv:.2f} Wh\n"
                        f"3. Gesamtkapazität = {effektiv:.2f} Wh ÷ {spannung:.2f} V = {gesamtkapazitaet:.2f} Ah\n"
                        f"4. Akkus = {gesamtkapazitaet:.2f} Ah ÷ {einzelakku:.2f} Ah = {akkus:.2f} → **{aufgerundet} Akkus benötigt**"
                    )

                case _:
                    raise ValueError("Unbekannte Zielgröße")

            embed.add_field(name="🧠 Rechenweg", value=f"```{rechenweg}```", inline=False)
            embed.add_field(name="✅ Ergebnis", value=f"**{ergebnis:.2f} {self.ziel}**", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print("🧪 FEHLER IM MODAL:")
            traceback.print_exc()
            print(f"Fehlermeldung: {e}")
            await interaction.response.send_message("❌ Es ist ein interner Fehler aufgetreten. Bitte überprüfe die Eingaben.", ephemeral=True)

class USVDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Kapazität", description="🔋 Kapazität (Ah) berechnen"),
            discord.SelectOption(label="Leistung", description="⚡ Leistung (W) berechnen"),
            discord.SelectOption(label="Zeit", description="⏱️ Laufzeit (min) berechnen"),
            discord.SelectOption(label="Spannung", description="🔌 Spannung (V) berechnen"),
            discord.SelectOption(label="Akkus", description="🔋 Akkuanzahl berechnen"),
            discord.SelectOption(label="Watt → VA", description="📐 W zu Scheinleistung umrechnen (×1.55)"),
            discord.SelectOption(label="VA → Watt", description="📉 Scheinleistung zu W umrechnen (×0.65)")
        ]
        super().__init__(
            placeholder="Wähle eine Zielgröße zur Berechnung",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        ziel = ZIEL_MAPPING.get(self.values[0].strip(), "Unbekannt")
        print(f"📥 Dropdown ausgewählt: {ziel} ({interaction.user.display_name})")
        await interaction.response.send_modal(USVInputModal(ziel))

class USVRechnerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(USVDropdown())

class USVFormelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="usv", description="Interaktive USV-Berechnung über Dropdown-Menü")
    async def usv(self, interaction: Interaction):
        embed = discord.Embed(
            title="🔧 USV Rechner – Was willst du berechnen?",
            description=(
                "Wähle eine Zielgröße zur Berechnung über das Dropdown-Menü.\n\n"
                "**Formeln:**\n"
                "• Kapazität = (W × Zeit) ÷ (V × Wirkungsgrad)\n"
                "• Watt = (Ah × V × Wirkungsgrad) ÷ Zeit\n"
                "• Zeit = (Ah × V × Wirkungsgrad) ÷ Watt\n"
                "• Spannung = (W × Zeit) ÷ (Ah × Wirkungsgrad)\n"
                "• Akkus = Gesamtkapazität ÷ Einzelakku\n"
                "• VA = W × 1.55\n"
                "• Watt = VA × 0.65"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=USVRechnerView(), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(USVFormelCog(bot))
