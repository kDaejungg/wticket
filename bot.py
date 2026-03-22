import discord
from discord import app_commands
import asyncio
import io
import json
import config

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

active_sessions = set()

def has_staff_role(interaction: discord.Interaction) -> bool:
    staff_role_id = config.get("STAFF_ROLE_ID")
    if not staff_role_id:
        return interaction.user.guild_permissions.administrator
    return any(role.id == staff_role_id for role in interaction.user.roles)

def not_configured(interaction: discord.Interaction) -> bool:
    """Returns True and sends a message if bot is not configured yet."""
    if not config.is_configured():
        return True
    return False

TICKET_TYPES = {
    "ticket":{
        "emoji": "🎫",
        "color": discord.Color.dark_grey(),
        "label": "Ticket",
        "questions": [
            "Describe your issue or request:",
        ],
    },
    "bug":{
        "emoji": "🐛",
        "color": discord.Color.red(),
        "label": "Bug Report",
        "questions": [
            "Briefly describe the bug:",
            "How did you trigger it? (step by step):",
            "What was the expected behaviour?:",
        ],
    },
    "feedback": {
        "emoji": "💡",
        "color": discord.Color.blue(),
        "label": "Feedback",
        "questions": [
            "Share your feedback:",
            "What improvement would you suggest?:",
        ],
    },
    "support": {
        "emoji": "🛠️",
        "color": discord.Color.green(),
        "label": "Support Request",
        "questions": [
            "Describe your issue:",
            "Have you tried solving this before?:",
        ],
    },
}

class TicketSetupModal(discord.ui.Modal):
    def __init__(self, ticket_type: str):
        self.ticket_type = ticket_type
        data = TICKET_TYPES[ticket_type]
        super().__init__(title=f"{data['emoji']} {data['label']} — Setup")

        self.embed_title = discord.ui.TextInput(
            label="Embed Title",
            default=f"{data['emoji']} {data['label']}",
            max_length=100,
        )
        self.embed_desc = discord.ui.TextInput(
            label="Embed Description",
            style=discord.TextStyle.paragraph,
            default=f"Click the button below to start a {data['label'].lower()}.",
            max_length=1000,
        )
        self.button_label = discord.ui.TextInput(
            label="Button Label",
            default=f"Open Ticket",
            max_length=80,
        )

        self.add_item(self.embed_title)
        self.add_item(self.embed_desc)
        self.add_item(self.button_label)

    async def on_submit(self, interaction: discord.Interaction):
        data = TICKET_TYPES[self.ticket_type]
        embed = discord.Embed(
            title=self.embed_title.value,
            description=self.embed_desc.value,
            color=data["color"],
        )
        embed.set_footer(text="WTicket")

        view = OpenTicketView(self.ticket_type, self.button_label.value)
        channel = bot.get_channel(config.get("TICKET_CHANNEL_ID"))

        if not channel:
            await interaction.response.send_message(
                "❌ Ticket channel not found. Run `/setup` first.", ephemeral=True
            )
            return

        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ Setup complete in {channel.mention}", ephemeral=True
        )

class OpenTicketView(discord.ui.View):
    def __init__(self, ticket_type: str, button_label: str):
        super().__init__(timeout=None)
        styles = {
            "bug": discord.ButtonStyle.danger,
            "feedback": discord.ButtonStyle.primary,
            "support": discord.ButtonStyle.success,
        }
        button = discord.ui.Button(
            label=button_label,
            style=styles.get(ticket_type, discord.ButtonStyle.secondary),
            custom_id=f"open_{ticket_type}",
        )
        button.callback = self.callback
        self.add_item(button)

    async def callback(self, interaction: discord.Interaction):
        ticket_type = interaction.data["custom_id"].replace("open_", "")
        await handle_ticket(interaction, ticket_type)

async def handle_ticket(interaction: discord.Interaction, ticket_type: str):
    user = interaction.user
    guild = interaction.guild

    if not config.is_configured():
        await interaction.response.send_message(
            "⚠️ Bot is not configured yet. Ask an admin to run `/setup`.", ephemeral=True
        )
        return

    if user.id in active_sessions:
        await interaction.response.send_message(
            "⚠️ You already have an active session.", ephemeral=True
        )
        return

    data = TICKET_TYPES[ticket_type]
    await interaction.response.send_message(
        f"{data['emoji']} Questions sent to your DMs!", ephemeral=True
    )

    active_sessions.add(user.id)
    try:
        answers = await ask_questions_dm(user, data)
    finally:
        active_sessions.discard(user.id)

    if not answers:
        return

    ticket_channel = bot.get_channel(config.get("TICKET_CHANNEL_ID"))
    if not ticket_channel:
        await interaction.followup.send(
            "❌ Ticket channel not found. Ask an admin to run `/setup`.",
            ephemeral=True,
        )
        return

    staff_role = guild.get_role(config.get("STAFF_ROLE_ID"))
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    category = ticket_channel.category  # None olabilir, create_text_channel None kategoriyi kabul eder
    channel = await guild.create_text_channel(
        name=f"{ticket_type}-{user.name}",
        category=category,
        overwrites=overwrites,
    )

    embed = discord.Embed(title=f"{data['label']} — {user.name}", color=data["color"])
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"User ID: {user.id}")
    for q, a in zip(data["questions"], answers):
        embed.add_field(name=f"❓ {q}", value=a or "*(empty)*", inline=False)

    ping_role_id = config.get("PING_ROLE_ID")
    ping = f"<@&{ping_role_id}>" if ping_role_id else ""
    await channel.send(content=f"{ping} {user.mention}", embed=embed)
    await channel.send(view=CloseTicketView(user.id))

async def ask_questions_dm(user: discord.User, data: dict):
    try:
        dm = await user.create_dm()
        intro = discord.Embed(
            title=f"{data['emoji']} {data['label']}",
            description="Answer each question. Type `cancel` to stop. (3 min per question)",
            color=data["color"],
        )
        await dm.send(embed=intro)

        answers = []
        for i, q in enumerate(data["questions"], 1):
            await dm.send(f"**{i}/{len(data['questions'])}.** {q}")
            msg = await bot.wait_for(
                "message",
                timeout=180,
                check=lambda m: m.author == user and m.guild is None,
            )
            if msg.content.lower() == "cancel":
                await dm.send("❌ Cancelled.")
                return None
            answers.append(msg.content)

        await dm.send("✅ Processing your ticket...")
        return answers
    except (discord.Forbidden, asyncio.TimeoutError):
        return None

class CloseTicketView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.secondary, custom_id="close_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (interaction.user.id == self.owner_id or has_staff_role(interaction)):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Closing and generating transcript...")

        log_str = f"Ticket Transcript: {interaction.channel.name}\n" + "=" * 30 + "\n"
        async for m in interaction.channel.history(limit=None, oldest_first=True):
            log_str += f"[{m.created_at.strftime('%Y-%m-%d %H:%M')}] {m.author}: {m.content}\n"

        file = discord.File(
            io.BytesIO(log_str.encode()),
            filename=f"transcript-{interaction.channel.name}.txt",
        )
        log_chan = bot.get_channel(config.get("LOG_CHANNEL_ID"))
        if log_chan:
            # Ensure bot can send to log channel regardless of channel permissions
            await log_chan.set_permissions(
                interaction.guild.me,
                send_messages=True,
                attach_files=True,
                view_channel=True,
            )
            await log_chan.send(file=file)

        await asyncio.sleep(3)
        await interaction.channel.delete()

@tree.command(name="setup", description="Configure WTicket (Admin only)")
@app_commands.describe(
    ticket_channel="Channel where ticket embeds will be posted",
    staff_role="Role that can manage tickets",
    log_channel="Channel where ticket transcripts will be sent (Staff only)",
    ping_role="Role to ping when a new ticket is opened (optional)",
)
async def setup(
    interaction: discord.Interaction,
    ticket_channel: discord.TextChannel,
    staff_role: discord.Role,
    log_channel: discord.TextChannel,
    ping_role: discord.Role = None,
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need Administrator permission to run this command.", ephemeral=True
        )
        return

    config.set("TICKET_CHANNEL_ID", ticket_channel.id)
    config.set("STAFF_ROLE_ID", staff_role.id)
    config.set("LOG_CHANNEL_ID", log_channel.id)
    config.set("PING_ROLE_ID", ping_role.id if ping_role else None)

    embed = discord.Embed(title="✅ WTicket Configured", color=discord.Color.green())
    embed.add_field(name="Ticket Channel", value=ticket_channel.mention, inline=False)
    embed.add_field(name="Log Channel", value=log_channel.mention, inline=False)
    embed.add_field(name="Staff Role", value=staff_role.mention, inline=False)
    embed.add_field(name="Ping Role", value=ping_role.mention if ping_role else "Not set", inline=False)
    embed.set_footer(text="You can now use /bugticket, /feedbackticket, /supportticket")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="ticket", description="Create a ticket embed (Staff only)")
async def bugticket(interaction: discord.Interaction):
    if not has_staff_role(interaction):
        await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
        return
    await interaction.response.send_modal(TicketSetupModal("ticket"))

@tree.command(name="bugticket", description="Create a bug report embed (Staff only)")
async def bugticket(interaction: discord.Interaction):
    if not has_staff_role(interaction):
        await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
        return
    await interaction.response.send_modal(TicketSetupModal("bug"))


@tree.command(name="feedbackticket", description="Create a feedback embed (Staff only)")
async def feedbackticket(interaction: discord.Interaction):
    if not has_staff_role(interaction):
        await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
        return
    await interaction.response.send_modal(TicketSetupModal("feedback"))


@tree.command(name="supportticket", description="Create a support request embed (Staff only)")
async def supportticket(interaction: discord.Interaction):
    if not has_staff_role(interaction):
        await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
        return
    await interaction.response.send_modal(TicketSetupModal("support"))



@tree.command(name="about", description="Show information about WTicket")
async def about(interaction: discord.Interaction):
    with open("about.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    embed = discord.Embed(
        title=f"✨ {data['bot_name']}",
        description=data["description"],
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Version", value=data["version"], inline=True)
    embed.add_field(name="Developer", value=data["developer"], inline=True)
    embed.add_field(name="Features", value="\n".join(f"• {f}" for f in data["features"]), inline=False)
    embed.add_field(name="Note", value=data["credits"], inline=False)
    embed.add_field(name="⚖️ " + data["license"], value="", inline=True)
    embed.add_field(name="GitHub", value=f"[Source Code]({data['github_repo']})", inline=True)
    embed.set_footer(text=f"Made with 🎫 by {data['developer']}")
    await interaction.response.send_message(embed=embed)

@tree.command(name="viewconfig", description="Show current bot configuration (Staff only)")
async def viewconfig(interaction: discord.Interaction):
    if not has_staff_role(interaction) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Access denied.", ephemeral=True)
        return

    embed = discord.Embed(title="⚙️ Current Configuration", color=discord.Color.blurple())
    ch_id = config.get("TICKET_CHANNEL_ID")
    log_id = config.get("LOG_CHANNEL_ID")
    sr_id = config.get("STAFF_ROLE_ID")
    pr_id = config.get("PING_ROLE_ID")
    embed.add_field(name="Ticket Channel", value=f"<#{ch_id}>" if ch_id else "Not set", inline=False)
    embed.add_field(name="Log Channel", value=f"<#{log_id}>" if log_id else "Not set", inline=False)
    embed.add_field(name="Staff Role", value=f"<@&{sr_id}>" if sr_id else "Not set", inline=False)
    embed.add_field(name="Ping Role", value=f"<@&{pr_id}>" if pr_id else "Not set", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    for t in TICKET_TYPES:
        bot.add_view(OpenTicketView(t, "Open Ticket"))
    bot.add_view(CloseTicketView(0))
    await tree.sync()

    # Create "WTicket" role in every guild if it doesn't exist, then assign to bot
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name="WTicket")
        if not role:
            role = await guild.create_role(name="WTicket", reason="WTicket bot role")
            print(f"✅ Created 'WTicket' role in {guild.name}")
        if role not in guild.me.roles:
            await guild.me.add_roles(role, reason="WTicket bot role")
            print(f"🎫 Assigned 'WTicket' role in {guild.name}")

    print(f"✅ Bot ready: {bot.user} ({bot.user.id})")
    if config.is_configured():
        print(f"📌 Ticket channel: {config.get('TICKET_CHANNEL_ID')}")
        print(f"🔐 Staff role: {config.get('STAFF_ROLE_ID')}")
    else:
        print("⚠️  Not configured yet — run /setup in Discord")
    print("⚡ Slash commands synced: /setup /bugticket /feedbackticket /supportticket /viewconfig /about")


bot.run(config.TOKEN)
