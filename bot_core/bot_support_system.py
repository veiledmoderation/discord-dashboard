import os
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

tickets_col = db["tickets"]
ticket_messages_col = db["ticket_messages"]
tickets_transcripts_col = db["tickets_transcripts"]
tickets_evidence_col = db["tickets_evidence"]

appeals_col = db["appeals"]
appeal_messages_col = db["appeal_messages"]

staff_reports_col = db["staff_reports"]
staff_report_notes_col = db["staff_report_notes"]

staff_col = db["staff"]


def now():
    return datetime.utcnow().isoformat()


def get_lowest_load_staff():
    staff = list(staff_col.find({"status": "active"}))
    if not staff:
        return None
    return sorted(staff, key=lambda s: s.get("tickets_total", 0))[0]


class SupportSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def notify_staff_dm(self, text):
        staff_members = staff_col.find({"status": "active"})
        for s in staff_members:
            user_id = int(s["user_id"])
            user = self.bot.get_user(user_id)
            if user:
                try:
                    await user.send(text)
                except:
                    pass

    # ===== TICKET CREATION =====
    @app_commands.command(name="ticket", description="Open a support ticket.")
    async def ticket(self, interaction: discord.Interaction, subject: str):
        ticket_id = str(interaction.id)

        tickets_col.insert_one({
            "id": ticket_id,
            "username": interaction.user.name,
            "user_id": str(interaction.user.id),
            "subject": subject,
            "status": "open",
            "opened_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "priority": "low"
        })

        ticket_messages_col.insert_one({
            "ticket_id": ticket_id,
            "time": now(),
            "text": subject,
            "author": interaction.user.name
        })

        assigned = get_lowest_load_staff()
        if assigned:
            tickets_col.update_one(
                {"id": ticket_id},
                {
                    "$set": {
                        "assigned_staff_id": assigned["user_id"],
                        "assigned_staff_name": assigned["username"]
                    }
                }
            )
            await self.notify_staff_dm(
                f"Ticket #{ticket_id} auto-assigned to {assigned['username']}"
            )

        await interaction.response.send_message(
            f"Your ticket has been created. ID: `{ticket_id}`",
            ephemeral=True
        )

        await self.notify_staff_dm(
            f"New ticket #{ticket_id} from {interaction.user.name}: {subject}"
        )

    # ===== TICKET TRANSCRIPT =====
    @app_commands.command(name="ticket_transcript", description="Generate a transcript for a ticket.")
    async def ticket_transcript(self, interaction: discord.Interaction, ticket_id: str):
        ticket = tickets_col.find_one({"id": ticket_id})
        if not ticket:
            await interaction.response.send_message("Ticket not found.", ephemeral=True)
            return

        messages = list(ticket_messages_col.find({"ticket_id": ticket_id}).sort("time", 1))

        transcript = {
            "ticket_id": ticket_id,
            "subject": ticket.get("subject", ""),
            "username": ticket.get("username", ""),
            "messages": messages,
            "generated_at": now()
        }

        tickets_transcripts_col.insert_one(transcript)

        await interaction.response.send_message(
            f"Transcript generated for ticket `{ticket_id}`.",
            ephemeral=True
        )

    # ===== TICKET EVIDENCE =====
    @app_commands.command(name="ticket_evidence", description="Attach evidence to a ticket.")
    async def ticket_evidence(self, interaction: discord.Interaction, ticket_id: str, url: str, note: str = ""):
        ticket = tickets_col.find_one({"id": ticket_id})
        if not ticket:
            await interaction.response.send_message("Ticket not found.", ephemeral=True)
            return

        tickets_evidence_col.insert_one({
            "ticket_id": ticket_id,
            "url": url,
            "note": note,
            "time": now()
        })

        await interaction.response.send_message(
            f"Evidence added to ticket `{ticket_id}`.",
            ephemeral=True
        )

        await self.notify_staff_dm(
            f"Evidence added to ticket #{ticket_id}: {url}"
        )

    # ===== TICKET PRIORITY =====
    @app_commands.command(name="ticket_priority", description="Set ticket priority.")
    async def ticket_priority(self, interaction: discord.Interaction, ticket_id: str, priority: str):
        if priority not in ["low", "medium", "high", "critical"]:
            await interaction.response.send_message("Invalid priority.", ephemeral=True)
            return

        tickets_col.update_one({"id": ticket_id}, {"$set": {"priority": priority}})

        await interaction.response.send_message(
            f"Priority for ticket `{ticket_id}` set to `{priority}`.",
            ephemeral=True
        )

        await self.notify_staff_dm(
            f"Ticket #{ticket_id} priority updated to {priority}"
        )

    # ===== APPEAL CREATION =====
    @app_commands.command(name="appeal", description="Submit a punishment appeal.")
    async def appeal(self, interaction: discord.Interaction, punishment_type: str, reason: str):
        appeal_id = str(interaction.id)

        appeals_col.insert_one({
            "id": appeal_id,
            "username": interaction.user.name,
            "user_id": str(interaction.user.id),
            "punishment_type": punishment_type,
            "reason": reason,
            "status": "open",
            "opened_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "messages": []
        })

        appeal_messages_col.insert_one({
            "appeal_id": appeal_id,
            "time": now(),
            "text": reason,
            "author": interaction.user.name
        })

        await interaction.response.send_message(
            f"Your appeal has been submitted. ID: `{appeal_id}`",
            ephemeral=True
        )

        await self.notify_staff_dm(
            f"New appeal #{appeal_id} from {interaction.user.name}: {punishment_type} — {reason}"
        )

    # ===== STAFF REPORT CREATION =====
    @app_commands.command(name="staff_report", description="Report a staff member.")
    async def staff_report(self, interaction: discord.Interaction, staff_member: discord.Member, reason: str):
        report_id = str(interaction.id)

        staff_reports_col.insert_one({
            "id": report_id,
            "reporter_name": interaction.user.name,
            "reporter_id": str(interaction.user.id),
            "staff_name": staff_member.name,
            "staff_id": str(staff_member.id),
            "reason": reason,
            "status": "pending",
            "opened_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "notes": []
        })

        staff_report_notes_col.insert_one({
            "report_id": report_id,
            "time": now(),
            "text": reason,
            "author": interaction.user.name
        })

        await interaction.response.send_message(
            f"Your staff report has been submitted. ID: `{report_id}`",
            ephemeral=True
        )

        await self.notify_staff_dm(
            f"New staff report #{report_id} against {staff_member.name}: {reason}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SupportSystem(bot))
