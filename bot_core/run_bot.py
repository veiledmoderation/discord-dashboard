import os
import threading

# -----------------------------------
# Import the bot instance
# -----------------------------------
from bot import bot

# -----------------------------------
# Import dashboard starter
# -----------------------------------
try:
    from app import start_dashboard
except Exception as e:
    print("[ERROR] Could not import dashboard:", e)
    start_dashboard = None

# -----------------------------------
# Launch dashboard in background
# -----------------------------------
def launch_dashboard():
    if start_dashboard:
        print("[DASHBOARD] Starting Flask dashboard on port 5000...")
        start_dashboard(host="0.0.0.0", port=5000, debug=False)
    else:
        print("[DASHBOARD] Dashboard import failed; skipping startup.")

threading.Thread(target=launch_dashboard, daemon=True).start()

# -----------------------------------
# Run the bot
# -----------------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
