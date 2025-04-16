
import discord
from discord.ext import commands
from discord import app_commands
import requests

class RaiderIOCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://raider.io/api/v1"

    @app_commands.command(name="character", description="Zeigt Informationen über einen WoW-Charakter an")
    @app_commands.describe(
        name="Der Name des Charakters",
        realm="Der Name des Realms",
        region="Die Region (EU/US)"
    )
    async def character(self, interaction: discord.Interaction, name: str, realm: str, region: str = "eu"):
        await interaction.response.defer(ephemeral=True)
        
        try:
            url = f"{self.base_url}/characters/profile"
            params = {
                "region": region,
                "realm": realm,
                "name": name,
                "fields": "mythic_plus_scores_by_season:current,mythic_plus_recent_runs:10,mythic_plus_best_runs:10,mythic_plus_scores,gear,raid_progression,thumbnail_url,faction"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "error" in data:
                await interaction.followup.send(f"❌ Fehler: Character nicht gefunden")
                return
                
            # Faction-based color (rot für Horde, blau für Allianz)
            faction = data.get("faction", "alliance").lower()
            embed_color = discord.Color.red() if faction == "horde" else discord.Color.blue()
            
            # Character thumbnail
            thumbnail_url = data.get("thumbnail_url", "")
            
            embed = discord.Embed(
                title=f"{data['name']} - {data['realm']} ({data['region'].upper()})",
                url=data['profile_url'],
                color=embed_color
            )
            
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
            
            if "mythic_plus_scores_by_season" in data:
                current_score = data["mythic_plus_scores_by_season"][0]["scores"]["all"]
                embed.add_field(name="M+ Score", value=f"{current_score:.1f}", inline=True)
            
            if "mythic_plus_recent_runs" in data:
                dungeon_icons = {
                    "De Other Side": "🎭",
                    "Halls of Atonement": "⛪",
                    "Mists of Tirna Scithe": "🌿",
                    "Plaguefall": "☠️",
                    "Sanguine Depths": "🩸",
                    "Spires of Ascension": "🏰",
                    "The Necrotic Wake": "💀",
                    "Theater of Pain": "🎭",
                    "Dawn of the Infinite": "⌛",
                    "Atal'Dazar": "🏯",
                    "Waycrest Manor": "🏛️",
                    "Black Rook Hold": "🏰",
                    "Darkheart Thicket": "🌳",
                    "The Everbloom": "🌺",
                    "Throne of the Tides": "🌊"
                }
                
                recent_runs = ""
                for run in data["mythic_plus_recent_runs"][:4]:
                    dungeon_name = run['dungeon']
                    icon = dungeon_icons.get(dungeon_name, "🗝️")
                    
                    # Format time
                    clear_time_ms = run.get('clear_time_ms', 0)
                    minutes = clear_time_ms // 60000
                    seconds = (clear_time_ms % 60000) // 1000
                    time_str = f"{minutes}:{seconds:02d}"
                    
                    # Add hyperlinked run information
                    run_url = run.get('url', '')
                    if run_url:
                        recent_runs += f"{icon} [{dungeon_name}]({run_url}) +{run['mythic_level']}"
                    else:
                        recent_runs += f"{icon} **{dungeon_name}** +{run['mythic_level']}"
                        
                    recent_runs += f" • {time_str} • {run['score']:.1f} Score"
                    
                    # Add affixes if available
                    if 'affixes' in run:
                        affixes = ' '.join(affix['name'] for affix in run['affixes'])
                        recent_runs += f"\n┗━ *{affixes}*"
                    
                    recent_runs += "\n\n"
                
                if recent_runs:
                    embed.add_field(name="📊 Letzte M+ Runs", value=recent_runs, inline=False)
                    
            # Add gear score if available
            if "gear" in data:
                gear_info = f"📱 **iLvl:** {data['gear'].get('item_level_equipped', 'N/A')}"
                embed.add_field(name="Ausrüstung", value=gear_info, inline=True)
                
            # Add season scores if available
            if "mythic_plus_scores" in data:
                scores = data["mythic_plus_scores"]
                score_info = f"🏆 **Overall:** {scores.get('all', 0):.1f}\n"
                score_info += f"⚔️ **DPS:** {scores.get('dps', 0):.1f}\n"
                score_info += f"🛡️ **Tank:** {scores.get('tank', 0):.1f}\n"
                score_info += f"💚 **Healer:** {scores.get('healer', 0):.1f}"
                embed.add_field(name="Season Scores", value=score_info, inline=True)
            
            view = discord.ui.View()
            view.add_item(CutoffButton())
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Ein Fehler ist aufgetreten: {str(e)}")

class CutoffButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🏆 Season Cutoffs", 
            style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            url = "https://raider.io/api/v1/mythic-plus/season-cutoffs?region=eu&season=season-tww-2"
            response = requests.get(url)
            data = response.json()

            embed = discord.Embed(
                title="🏆 Mythic+ Season Cutoffs (EU)",
                color=discord.Color.gold()
            )

            # Strukturiere die Cutoff-Daten für p999 und p990
            cutoffs = {
                "Top 0.1% (p999)": data.get("p999", {}).get("quantileMinValue", 0),
                "Top 1% (p990)": data.get("p990", {}).get("quantileMinValue", 0)
            }

            for title, score in cutoffs.items():
                # Format score to 1 decimal place
                score = round(float(score), 1)
                
                embed.add_field(
                    name=title,
                    value=f"📊 Score: {score}",
                    inline=True
                )

            embed.set_footer(text="Daten von Raider.IO • Season TWW Season 2")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Ein Fehler ist aufgetreten: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RaiderIOCog(bot))
