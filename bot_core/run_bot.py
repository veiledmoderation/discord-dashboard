import os
import threading
from dotenv import load_dotenv

load_dotenv()

# Correct import paths for repo structure
from bot_core.bot import bot

try:
    from dashboard.app import start_dashboard
except Exception as e:
        print("[ERROR] Could not import dashboard:", e)
        start_dashboard = None

def launch_dashboard():
    if start_dashboard:
        print("[DASHBOARD] Starting Flask dashboard...")

        # Railway requires PORT from environment
        port = int(os.environ.get("PORT", 5000))

        start_dashboard(
            host="0.0.0.0",
            port=port,
            debug=False
        )
    else:
        print("[DASHBOARD] Dashboard import failed; skipping startup.")

# Run dashboard in background thread
threading.Thread(target=launch_dashboard, daemon=True).start()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
