import discord
from discord.ext import commands
from discord import app_commands, Interaction
from modules.quiz_manager import QuizManager
import os
import asyncio
import random

LF_MAPPING = {
    "LF1": "Lernfeld 1: Grundlagen der IT-Systeme",
    "LF2": "Lernfeld 2: Vernetzte Systeme einrichten",
    "LF3": "Lernfeld 3: Systeme zur Datenverarbeitung",
    "LF4": "Lernfeld 4: IT-Sicherheit und Datenschutz",
    "LF5": "Lernfeld 5: Benutzerunterstützung und Support"
}

OPTION_LETTERS = ["A", "B", "C", "D"]
QUIZ_CHANNEL_ID = 1359197662443737400

class QuizSelect(discord.ui.Select):
    def __init__(self, cog, user_id):
        options = [
            discord.SelectOption(label=v.split(":")[0], description=v.split(":")[1], value=k)
            for k, v in LF_MAPPING.items()
        ]
        super().__init__(placeholder="Wähle ein Lernfeld für dein Quiz...", options=options)
        self.cog = cog
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("🚫 Das ist nicht dein Auswahlmenü!", ephemeral=True)

        try:
            print(f"📝 Quiz gestartet für User {interaction.user.id}")
            print(f"📚 Gewähltes Lernfeld: {self.values[0]}")
            
            await interaction.response.defer()
            
            # Teste Datenbankverbindung
            fragen = self.cog.manager.hole_alle_fragen(self.values[0])
            print(f"📊 Anzahl geladener Fragen: {len(fragen) if fragen else 0}")
            
            if not fragen:
                await interaction.followup.send("❌ Keine Fragen in der Datenbank gefunden!", ephemeral=True)
                return
                
            await self.cog.start_quiz(interaction, self.values[0], replace=True)
            print("✅ Quiz erfolgreich gestartet")
            
        except Exception as e:
            print(f"❌ Fehler beim Starten des Quiz: {str(e)}")
            await interaction.followup.send(
                f"❌ Fehler beim Laden des Quiz: {str(e)}", 
                ephemeral=True
            )


class StatsButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="📊 Meine Statistik anzeigen", style=discord.ButtonStyle.secondary)
        self.cog = cog

    async def callback(self, interaction: Interaction):
        stats = self.cog.manager.hole_statistik(interaction.user.id)
        if not stats:
            return await interaction.response.send_message("Du hast noch keine Fragen beantwortet.", ephemeral=True)

        text = ""
        # Sortiere nach Lernfeld-Nummer
        for lf in sorted(LF_MAPPING.keys()):
            if lf in stats:
                daten = stats[lf]
                gesamt = daten['gesamt']
                richtig = daten['richtig']
                prozent = (richtig / gesamt) * 100 if gesamt > 0 else 0
                text += f"{lf}: {richtig}/{gesamt} richtig ({prozent:.1f}%)\n"

        embed = discord.Embed(title="📊 Deine Quiz-Statistik", description=text, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EndButton(discord.ui.Button):
    def __init__(self, user_id=None):
        super().__init__(label="Beenden", style=discord.ButtonStyle.danger, row=1)
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        if self.user_id and interaction.user.id != self.user_id:
            return await interaction.response.send_message("🚫 Du darfst dieses Quiz nicht beenden.", ephemeral=True)
        await interaction.message.delete()


class QuizViewSelector(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.add_item(QuizSelect(cog, user_id))
        self.add_item(StatsButton(cog))
        self.add_item(LeaderboardButton())
        self.add_item(EndButton(user_id))


class BackToMenuButton(discord.ui.Button):
    def __init__(self, cog, user_id):
        super().__init__(label="Zurück zur Auswahl", style=discord.ButtonStyle.secondary, row=1)
        self.cog = cog
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("🚫 Das ist nicht dein Quiz.", ephemeral=True)

        await interaction.response.defer()
        beschreibung = "\n".join([f"**{v.split(':')[0]}**: {v.split(':')[1]}" for v in LF_MAPPING.values()])
        embed = discord.Embed(
            title="📚 Wähle ein Lernfeld",
            description=beschreibung,
            color=discord.Color.teal()
        )
        await interaction.message.edit(embed=embed, view=QuizViewSelector(self.cog, self.user_id))


class LeaderboardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="📊 Leaderboard",
            style=discord.ButtonStyle.secondary,
            row=2
        )

    async def callback(self, interaction: Interaction):
        conn = interaction.client.get_cog("QuizCog").manager.get_connection()
        cur = conn.cursor()
        
        try:
            # Hole Statistiken aus der Datenbank
            cur.execute("""
                SELECT user_id, 
                       SUM(richtig) as total_correct,
                       SUM(gesamt) as total_questions
                FROM quiz_progress
                GROUP BY user_id
                HAVING SUM(gesamt) > 0
                ORDER BY CAST(SUM(richtig) AS FLOAT) / CAST(SUM(gesamt) AS FLOAT) DESC, 
                         SUM(richtig) DESC
                LIMIT 10
            """)
            
            stats = cur.fetchall()
            
            # Erstelle Embed
            embed = discord.Embed(
                title="🏆 Quiz Leaderboard",
                description="Die Top 10 Quizspieler:",
                color=discord.Color.gold()
            )
            
            for i, (user_id, correct, total) in enumerate(stats, 1):
                try:
                    user = await interaction.client.fetch_user(int(user_id))
                    accuracy = (correct / total) * 100
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {user.name}",
                        value=f"✅ {correct}/{total} richtig ({accuracy:.1f}%)",
                        inline=False
                    )
                except:
                    continue
                    
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ Fehler beim Laden des Leaderboards: {e}")
            await interaction.response.send_message("❌ Fehler beim Laden des Leaderboards", ephemeral=True)
            
        finally:
            cur.close()
            conn.close()

class JokerButton(discord.ui.Button):
    def __init__(self, user_id, is_used=False):
        super().__init__(
            label="50/50 Joker", 
            style=discord.ButtonStyle.secondary if is_used else discord.ButtonStyle.success,
            row=2,
            disabled=is_used
        )
        self.user_id = user_id
        
    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("🚫 Das ist nicht dein Quiz!", ephemeral=True)
            
        view = self.view
        frage = view.fragen_liste[view.index]
        richtig_index = frage.get("richtig", 0)
        
        # Setze den Joker-Status global
        view.joker_used = True
        self.disabled = True
        self.style = discord.ButtonStyle.secondary
        
        # Wähle zufällig zwei falsche Antworten zum Durchstreichen
        falsche_indices = [i for i in range(4) if i != richtig_index]
        zu_entfernen = random.sample(falsche_indices, 2)
        
        # Durchstreiche die ausgewählten Antworten
        for child in view.children:
            if isinstance(child, QuizButton):
                if child.index in zu_entfernen:
                    child.disabled = True
                    child.label = f"~~{child.label}~~"
        
        await interaction.response.edit_message(view=view)

class QuizView(discord.ui.View):
    def __init__(self, fragen_liste, index, lernfeld, punkte_gesamt, punkte_max, user_id, cog, joker_used=False):
        super().__init__(timeout=None)
        self.fragen_liste = fragen_liste
        self.index = index
        self.lernfeld = lernfeld
        self.punkte_gesamt = punkte_gesamt
        self.punkte_max = punkte_max
        self.user_id = user_id
        self.joker_used = joker_used

        frage = fragen_liste[index]
        for i, buchstabe in enumerate(OPTION_LETTERS):
            self.add_item(QuizButton(buchstabe, i, frage, self))
        self.add_item(JokerButton(user_id, self.joker_used))
        self.add_item(EndButton(user_id))
        self.add_item(BackToMenuButton(cog, user_id))


class QuizButton(discord.ui.Button):
    def __init__(self, label, index, frage, quiz_view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.index = index
        self.frage = frage
        self.quiz_view = quiz_view

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.quiz_view.user_id:
            return await interaction.response.send_message("🚫 Das ist nicht dein Quiz!", ephemeral=True)

        richtig_index = self.frage["richtig"]
        ist_richtig = self.index == richtig_index
        punkte = self.frage["punkte"]

        feedback = (
            f"✅ **Richtig!** {OPTION_LETTERS[self.index]} war korrekt. (+{punkte} Punkte)"
            if ist_richtig else
            f"❌ **Falsch.** Du hast {OPTION_LETTERS[self.index]} gewählt. Richtig wäre {OPTION_LETTERS[richtig_index]}. (+0 Punkte)"
        )

        if ist_richtig:
            self.quiz_view.punkte_gesamt += punkte
        self.quiz_view.punkte_max += punkte

        try:
            # Debug print
            print(f"Speichere Fortschritt: User={interaction.user.id}, LF={self.quiz_view.lernfeld}, Richtig={ist_richtig}")
            interaction.client.get_cog("QuizCog").manager.speichere_fortschritt(
                interaction.user.id, self.quiz_view.lernfeld, ist_richtig
            )
            print("✅ Fortschritt erfolgreich gespeichert")
        except Exception as e:
            print(f"❌ Fehler beim Speichern des Fortschritts: {e}")

        feedback_msg = await interaction.response.send_message(feedback, ephemeral=True)
        await asyncio.sleep(3)
        try:
            await interaction.delete_original_response()
        except:
            pass

        self.quiz_view.index += 1
        if self.quiz_view.index >= len(self.quiz_view.fragen_liste):
            prozent = (self.quiz_view.punkte_gesamt / self.quiz_view.punkte_max) * 100 if self.quiz_view.punkte_max > 0 else 0
            summary = (
                f"🏁 **Quiz beendet!**\n"
                f"**Punkte:** {self.quiz_view.punkte_gesamt}/{self.quiz_view.punkte_max} ({prozent:.1f}%)"
            )

            stats = interaction.client.get_cog("QuizCog").manager.hole_statistik(interaction.user.id)
            statistik_text = ""
            if self.quiz_view.lernfeld in stats:
                richtig = stats[self.quiz_view.lernfeld]["richtig"]
                gesamt = stats[self.quiz_view.lernfeld]["gesamt"]
                anteil = (richtig / gesamt) * 100 if gesamt > 0 else 0
                statistik_text = f"\n📊 **Deine Statistik für {self.quiz_view.lernfeld}**: {richtig}/{gesamt} richtig ({anteil:.1f}%)"

            embed = discord.Embed(title="📊 Ergebnis", description=summary + statistik_text, color=discord.Color.green())
            view = discord.ui.View()
            view.add_item(BackToMenuButton(interaction.client.get_cog("QuizCog"), self.quiz_view.user_id))
            await interaction.message.edit(embed=embed, view=view)
            return

        neue_frage = self.quiz_view.fragen_liste[self.quiz_view.index]
        beschreibung = f"**Frage {self.quiz_view.index+1} von {len(self.quiz_view.fragen_liste)}**\n"
        beschreibung += f"🧠 Wert: {neue_frage.get('punkte', 1)} Punkte\n\n"
        beschreibung += f"**{neue_frage['frage']}**\n\n"
        for i, antwort in enumerate(neue_frage['antworten']):
            beschreibung += f"{OPTION_LETTERS[i]}. {antwort}\n\n"

        embed = discord.Embed(
            title=f"❓ Quizfrage aus {self.quiz_view.lernfeld}",
            description=beschreibung,
            color=discord.Color.blurple()
        )

        await interaction.message.edit(embed=embed, view=QuizView(
            self.quiz_view.fragen_liste,
            self.quiz_view.index,
            self.quiz_view.lernfeld,
            self.quiz_view.punkte_gesamt,
            self.quiz_view.punkte_max,
            self.quiz_view.user_id,
            interaction.client.get_cog("QuizCog"),
            self.quiz_view.joker_used
        ))


class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = QuizManager()

    @app_commands.command(name="quiz", description="Starte dein Quiz durch Auswahl eines Lernfelds")
    async def quiz(self, interaction: Interaction):
        if interaction.channel.id != QUIZ_CHANNEL_ID:
            return await interaction.response.send_message(
                f"❗ Bitte verwende diesen Befehl nur im <#{QUIZ_CHANNEL_ID}> Channel.", ephemeral=True)

        beschreibung = "\n".join([f"**{v.split(':')[0]}**: {v.split(':')[1]}" for v in LF_MAPPING.values()])
        embed = discord.Embed(
            title="📚 Wähle ein Lernfeld",
            description=beschreibung,
            color=discord.Color.teal()
        )
        view = QuizViewSelector(self, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

    async def start_quiz(self, interaction: Interaction, lernfeld: str, replace=False):
        fragen = self.manager.hole_alle_fragen(lernfeld)
        if not fragen:
            await interaction.response.send_message("❌ Keine Fragen für dieses Lernfeld gefunden.", ephemeral=True)
            return

        beschreibung = f"**Frage 1 von {len(fragen)}**\n"
        beschreibung += f"🧠 Wert: {fragen[0].get('punkte', 1)} Punkte\n\n"
        beschreibung += f"**{fragen[0]['frage']}**\n\n"
        for i, antwort in enumerate(fragen[0]['antworten']):
            beschreibung += f"{OPTION_LETTERS[i]}. {antwort}\n\n"

        embed = discord.Embed(
            title=f"❓ Quizfrage aus {lernfeld}",
            description=beschreibung,
            color=discord.Color.blurple()
        )

        view = QuizView(fragen, 0, lernfeld, 0, 0, interaction.user.id, self)

        await interaction.message.edit(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(QuizCog(bot))