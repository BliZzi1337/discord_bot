import os
import asyncio
import discord
import datetime
import traceback
from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import web
from modules.websocket_handler import WebSocketHandler

start_time = None

# .env laden
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents setzen
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.presences = True  # Enable presence updates

# Bot-Instanz erstellen (nur einmal!)
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔁 Status-Rotation
async def status_loop():
    await bot.wait_until_ready()
    status_list = [
        discord.Activity(type=discord.ActivityType.watching, name="Binär umwandeln 🧠"),
        discord.Activity(type=discord.ActivityType.playing, name="mit Bytes rechnen 💾"),
        discord.Activity(type=discord.ActivityType.listening, name="/convert nutzen 🔁"),
        discord.Activity(type=discord.ActivityType.watching, name="deinen Input 👀"),
    ]
    index = 0
    while not bot.is_closed():
        await bot.change_presence(status=discord.Status.online, activity=status_list[index])
        index = (index + 1) % len(status_list)
        await asyncio.sleep(30)

# 🔁 Slash-Commands synchronisieren

@bot.event
async def on_ready():
    print("\n🤖 BOT STARTET...")
    print(f"Debug: Bot ist {bot.user} (ID: {bot.user.id})")
    print(f"Debug: In {len(bot.guilds)} Servern")
    print("\n🔄 SYNCHRONISIERE SLASH-COMMANDS...")

    try:
        print("Debug: Starte Command Sync...")

        # Sammle alle Commands
        all_commands = []
        for cog in bot.cogs.values():
            for command in cog.get_app_commands():
                all_commands.append(command.name)
        print(f"Debug: Gefundene Commands: {', '.join(all_commands)}")

        # Guild Commands synchronisieren (DAA Server)
        guild = discord.Object(id=1107964583928418324)
        print(f"Debug: Synchronisiere für Guild {guild.id}...")
        bot.tree.copy_global_to(guild=guild)
        guild_sync = await bot.tree.sync(guild=guild)

        # Global Commands synchronisieren
        print("Debug: Synchronisiere global...")
        synced = await bot.tree.sync()

        print(f"\n✨ SLASH-COMMANDS ERFOLGREICH SYNCHRONISIERT:")
        print(f"➡️ Guild Commands: {len(guild_sync)}")
        print(f"➡️ Global Commands: {len(synced)}")
        print(f"\n🤖 Bot ist erfolgreich eingeloggt als {bot.user}")
        print(f"🌐 In {len(bot.guilds)} Server(n)")
        print(f"📊 Latenz: {round(bot.latency * 1000)}ms\n")

    except Exception as e:
        print(f"❌ Fehler beim Command-Sync:")
        print(f"➡️ {str(e)}")
        print(f"➡️ {traceback.format_exc()}")

    #print(f"🤖 Bot ist online als {bot.user}")

# 🔌 Lade alle Cogs aus /cogs
async def load_all_cogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            modulename = file[:-3]
            try:
                await bot.load_extension(f"cogs.{modulename}")
                print(f"✅ Geladen: cogs.{modulename}")
            except Exception as e:
                print(f"❌ Fehler beim Laden von cogs.{modulename}: {e}")

# ⚙️ Lade alle Module aus /modules (nur die mit setup)
async def load_all_modules():
    exclude = ["quiz_manager", "chat_ai"]  # Hilfsmodule ohne setup() hier ausschließen
    for file in os.listdir("modules"):
        if file.endswith(".py") and not file.startswith("_"):
            modulename = file[:-3]
            if modulename in exclude:
                continue
            try:
                await bot.load_extension(f"modules.{modulename}")
                print(f"✅ Geladen: modules.{modulename}")
            except Exception as e:
                print(f"❌ Fehler beim Laden von modules.{modulename}: {e}")

# 🧠 Main-Logik
async def main():
    global start_time
    start_time = datetime.datetime.now(datetime.UTC)

    # Initialize bot but don't start yet
    bot.websocket_handler = WebSocketHandler()

    async def health_handler(request):
        bot_name = str(bot.user) if bot.user else "Initializing..."
        created_at = bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S') if bot.user else "Not available"
        guild_count = len(bot.guilds) if bot.is_ready() else 0
        status = "Online" if bot.is_ready() else "Initializing"

        # Get online stats for specific server (excluding bots)
        target_guild_id = 1335923619242577971
        online_count = 0
        if bot.is_ready():
            guild = bot.get_guild(target_guild_id)
            if guild:
                for member in guild.members:
                    status = getattr(member, 'status', discord.Status.offline)
                    if not member.bot and status != discord.Status.offline:
                        online_count += 1

        # Sammle aktive Voice-Nutzer
        voice_users = []
        if bot.is_ready():
            for guild in bot.guilds:
                for vc in guild.voice_channels:
                    for member in vc.members:
                        voice_users.append({
                            'name': member.display_name,
                            'channel': vc.name,
                            'server': guild.name,
                            'avatar_url': str(member.avatar.url) if member.avatar else '',
                            'is_muted': member.voice.self_mute
                        })

        # Calculate uptime
        if start_time:
            now = datetime.datetime.now(datetime.UTC)
            uptime = now - start_time
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            uptime_str = f"{days} Tage, {hours} Stunden, {minutes} Minuten"
        else:
            uptime_str = "Initialisiere..."

        def get_quiz_leaderboard_html():
            # Quiz-Manager initialisieren
            from modules.quiz_manager import QuizManager
            manager = QuizManager()

            # Statistiken sammeln
            stats = []
            with manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, 
                               SUM(richtig) as total_correct,
                               SUM(gesamt) as total_questions
                        FROM quiz_progress
                        GROUP BY user_id
                        HAVING SUM(gesamt) > 0
                    """)
                    for row in cur.fetchall():
                        user_id, total_correct, total_questions = row
                        accuracy = (total_correct / total_questions) * 100
                        stats.append((user_id, total_correct, total_questions, accuracy))

            # Nach Genauigkeit und richtigen Antworten sortieren
            stats.sort(key=lambda x: (x[3], x[1]), reverse=True)

            # HTML generieren
            html = []
            for i, (user_id, correct, total, accuracy) in enumerate(stats[:10], 1):
                try:
                    guild = bot.get_guild(1335923619242577971)
                    if guild:
                        member = guild.get_member(int(user_id))
                        username = member.display_name if member else f"User {user_id}"
                    else:
                        user = bot.get_user(int(user_id))
                        username = user.name if user else f"User {user_id}"
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    html.append(f"""
                        <div class="quiz-card">
                            <span class="quiz-medal">{medal}</span>
                            <div class="quiz-info">
                                <span class="quiz-name">{username}</span><br>
                                <span>✅ {correct}/{total} richtig ({accuracy:.1f}%)</span>
                            </div>
                        </div>
                    """)
                except:
                    continue

            return "".join(html) if html else "<div class='quiz-card'>Noch keine Quiz-Ergebnisse verfügbar</div>"

        # Generate dynamic content
        voice_users_html = "".join(
            f'<div class="user-card" data-speaking="false">'
            f'<img src="{user.get("avatar_url", "")}" class="user-avatar" onerror="this.style.display=\'none\'"/>'
            f'{"🔇" if user["is_muted"] else "🎙️"}︱🏠 {user["server"]}︱{user["channel"]}︱{user["name"]}'
            f'</div>'
            for user in voice_users
        ) if voice_users else '<p>Keine Nutzer in Voice-Channels</p>'
        quiz_leaderboard_html = get_quiz_leaderboard_html()

        # Read template and fill in variables
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template = f.read()

        status_str = str(status).lower()
        html = template.replace("{status}", str(status))\
            .replace("{status_lower}", status_str)\
            .replace("{bot_name}", bot_name)\
            .replace("{uptime_str}", uptime_str)\
            .replace("{guild_count}", str(guild_count))\
            .replace("{voice_users_html}", voice_users_html)\
            .replace("{quiz_leaderboard_html}", quiz_leaderboard_html)\
            .replace("{online_count}", str(online_count))
        return web.Response(text=html, content_type='text/html')

    # Setup and start web server first
    # Initialize web application with explicit host
    app = web.Application()
    app.router.add_get('/', health_handler)
    app.router.add_get('/ws', bot.websocket_handler.handle_connection)
    app.router.add_static('/templates', 'templates')

    # Setup web server with explicit host binding
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Started health check server on 0.0.0.0:8080")

    # Now start the bot
    async with bot:

        # Start the bot
        status_task = bot.loop.create_task(status_loop())
        try:
            await load_all_modules()
            await load_all_cogs()
            await bot.start(TOKEN)
        finally:
            if status_task and not status_task.cancelled():
                status_task.cancel()

# 🟢 Starte den Bot
if __name__ == "__main__":
    bot.websocket_handler = WebSocketHandler()  # Initialize WebSocket handler
    asyncio.run(main())