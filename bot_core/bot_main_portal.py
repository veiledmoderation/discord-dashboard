import discord
from discord.ext import commands
from discord import app_commands

MAIN_SERVER_ID = 111111111111111111          # main server ID
SUPPORT_SERVER_ID = 222222222222222222       # support server ID
SUPPORT_INVITE = "https://discord.gg/your-support-invite"


class MainPortal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def is_main_server(self, interaction: discord.Interaction) -> bool:
        return interaction.guild and interaction.guild.id == MAIN_SERVER_ID

    @app_commands.command(name="support", description="Open the Rituals Support Portal.")
    async def support(self, interaction: discord.Interaction):
        if not self.is_main_server(interaction):
            await interaction.response.send_message(
                "This command is only available in the main server.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Rituals Support Portal",
            description=(
                "All tickets, appeals, and staff reports are handled **only** in the "
                "**Rituals Support Server**.\n\n"
                "Click the button below to join and open a ticket."
            ),
            color=0x00eaff
        )
        embed.add_field(
            name="What you can do there:",
            value=(
                "• Open support tickets\n"
                "• Appeal bans and punishments\n"
                "• Contact Support Department\n"
                "• Submit staff reports"
            ),
            inline=False
        )

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Join Support Server",
                url=SUPPORT_INVITE,
                style=discord.ButtonStyle.link
            )
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.command(name="ticket")
    async def ticket_legacy(self, ctx: commands.Context):
        if ctx.guild and ctx.guild.id == MAIN_SERVER_ID:
            await ctx.reply(
                f"Tickets can only be opened in the Rituals Support Server.\n"
                f"Join here: {SUPPORT_INVITE}"
            )
        else:
            await ctx.reply("Use the ticket system in the Rituals Support Server.")

    @commands.command(name="appeal")
    async def appeal_legacy(self, ctx: commands.Context):
        if ctx.guild and ctx.guild.id == MAIN_SERVER_ID:
            await ctx.reply(
                f"Punishment appeals can only be opened in the Rituals Support Server.\n"
                f"Join here: {SUPPORT_INVITE}"
            )
        else:
            await ctx.reply("Use the appeal system in the Rituals Support Server.")


async def setup(bot: commands.Bot):
    await bot.add_cog(MainPortal(bot))
