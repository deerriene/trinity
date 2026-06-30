import discord
import io
from discord import app_commands

# ========= CONFIG =========
TICKET_CATEGORY_ID = 1519885556006391851
STAFF_ROLE_ID = 1520117326551449730
TICKET_LOG_CHANNEL_ID = 1520118378063204352
# ==========================


# ==========================
# TRANSCRIPT
# ==========================
async def gerar_transcript(channel: discord.TextChannel):
    messages = []

    async for msg in channel.history(oldest_first=True, limit=None):
        time = msg.created_at.strftime("%d/%m/%Y %H:%M")
        content = msg.content if msg.content else "[anexo/mídia]"
        messages.append(f"[{time}] {msg.author}: {content}")

    texto = "\n".join(messages)

    return discord.File(
        fp=io.BytesIO(texto.encode("utf-8")),
        filename=f"transcript-{channel.name}.txt"
    )


# ==========================
# BOTÃO FECHAR TICKET
# ==========================
class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Fechar Ticket",
            emoji="🔒",
            style=discord.ButtonStyle.red,
            custom_id="fechar_ticket"
        )

    async def callback(self, interaction: discord.Interaction):

        staff = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ Apenas a equipe pode fechar tickets.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "🔒 Fechando ticket e gerando transcript...",
            ephemeral=True
        )

        # gera transcript
        transcript = await gerar_transcript(interaction.channel)

        # envia log
        log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if log_channel:
            await log_channel.send(
                content=(
                    f"🧾 Ticket fechado\n"
                    f"📌 Canal: {interaction.channel.name}\n"
                    f"👤 Fechado por: {interaction.user.mention}"
                ),
                file=transcript
            )

        # apaga canal
        await interaction.channel.delete()


# ==========================
# VIEW DO TICKET
# ==========================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())


# ==========================
# BOTÃO ABRIR TICKET
# ==========================
class OpenTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Abrir Ticket",
            emoji="🎫",
            style=discord.ButtonStyle.green,
            custom_id="abrir_ticket"
        )

    async def callback(self, interaction: discord.Interaction):

        categoria = interaction.guild.get_channel(TICKET_CATEGORY_ID)

        if not isinstance(categoria, discord.CategoryChannel):
            return await interaction.response.send_message(
                "❌ Categoria inválida.",
                ephemeral=True
            )

        # anti-duplicação
        for canal in interaction.guild.text_channels:
            if canal.topic == str(interaction.user.id):
                return await interaction.response.send_message(
                    f"❌ Você já tem um ticket: {canal.mention}",
                    ephemeral=True
                )

        staff = interaction.guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        if staff:
            overwrites[staff] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )

        canal = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=categoria,
            topic=str(interaction.user.id),
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket criado",
            description=(
                f"Olá {interaction.user.mention}!\n\n"
                "Explique seu problema e aguarde a equipe."
            ),
            color=0x5865F2
        )

        await canal.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {canal.mention}",
            ephemeral=True
        )


# ==========================
# PAINEL DE TICKETS
# ==========================
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OpenTicketButton())


@app_commands.command(
    name="painel",
    description="Enviar painel de tickets"
)
@app_commands.checks.has_permissions(administrator=True)
async def painel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 Central de Tickets",
        description="Clique no botão abaixo para abrir um ticket.",
        color=0xffffff
    )

    embed.add_field(
        name="📌 Regras",
        value=(
            "• Descreva seu problema\n"
            "• Não abra tickets duplicados\n"
            "• Aguarde a equipe responder"
        ),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        view=TicketPanelView()
    )
