import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

DISCORD_API = "https://discord.com/api/v10"
