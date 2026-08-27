# VeilMod Dashboard & Discord Bot
A combined Flask dashboard + Discord moderation bot running together inside one process. The dashboard provides staff tools, logs, QnA editing, autorole settings, announcements, ping‑everyone, and ticket management. The bot handles moderation, QnA forwarding, autorole, announcements, and slash commands. Designed to run 24/7 on Railway using a single container.

## Project Structure
app.py (Flask dashboard)  
bot.py (Discord bot)  
run_bot.py (starts bot + dashboard together)  
moderation.py, moderation_logs.py, moderation_activity.py  
qa.py, autorole.py, announcements.py, ping_everyone.py  
templates/ (HTML)  
static/ (CSS, JS)  
requirements.txt  
Procfile  
Dockerfile  
README.md  

## Features
Dashboard: staff profiles, ticket system, QnA editor, autorole config, announcement system (channel selection + history), ping everyone, live logs, settings sync, API endpoints.  
Bot: prefix commands (!ban, !kick, !warn, !announce, !pingall), slash commands (/ban, /kick, /warn, /announce, /pingall), QnA forwarding, autorole, welcome messages, announcement posting, ping everyone posting, moderation logs, channel syncing for dashboard dropdowns.

## Environment Variables
DISCORD_BOT_TOKEN  
MONGO_URI  
RITUALS_GUILD_ID  
QUESTIONS_CHANNEL_ID  
UNANSWERED_CHANNEL_ID  
PING_CHANNEL_ID  
LOG_CHANNEL_ID  
STAFF_ROLE_ID  
AUTOROLE_ROLE_ID  
TICKET_CATEGORY_ID  

## Installation
Install dependencies:  
`pip install -r requirements.txt`  
Run bot + dashboard:  
`python run_bot.py`  
Dashboard URL:  
`http://localhost:5000`

## Dockerfile
FROM python:3.11-slim  
WORKDIR /app  
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt  
COPY . .  
ENV PYTHONUNBUFFERED=1  
CMD ["python", "run_bot.py"]

## Procfile
web: python run_bot.py

## Railway Deployment
1. Push project to GitHub  
2. Go to https://railway.app/dashboard  
3. Create New Project → Deploy from GitHub  
4. Add environment variables  
5. Railway builds Dockerfile and runs `python run_bot.py`  
6. Dashboard becomes public at:  
`https://yourproject.up.railway.app`  
7. Bot stays online 24/7  
8. Announcement system works automatically (bot syncs channels → dashboard loads → dashboard saves → bot posts)

## License
MIT License

## Credits
Created by **Veil**.
