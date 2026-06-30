import discord
from discord import app_commands

# ========= CONFIGURE =========
TICKET_CATEGORY_ID = 1519885556006391851
STAFF_ROLE_ID = 1520117326551449730
# =============================


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.green,
        custom_id="abrir_ticket"
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        categoria = interaction.guild.get_channel(TICKET_CATEGORY_ID)

        if categoria is None:
            await interaction.response.send_message(
                "❌ Categoria não encontrada.",
                ephemeral=True
            )
            return

        # Verifica se o usuário já possui um ticket
        for canal in categoria.text_channels:
            if canal.topic == str(interaction.user.id):
                await interaction.response.send_message(
                    f"Você já possui um ticket: {canal.mention}",
                    ephemeral=True
                )
                return

        staff = interaction.guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True
            ),

            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True
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
                "Explique o seu problema.\n"
                "Nossa equipe responderá em breve."
            ),
            color=0x5865F2
        )

        await canal.send(
            content=f"{interaction.user.mention}",
            embed=embed
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {canal.mention}",
            ephemeral=True
        )


@app_commands.command(
    name="painel",
    description="Enviar painel de tickets"
)
@app_commands.checks.has_permissions(administrator=True)
async def painel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Central de Atendimento",
        description=(
            "Bem-vindo ao sistema de tickets.\n\n"
            "Se precisar de ajuda, clique no botão abaixo para abrir um atendimento.\n"
            "Nossa equipe responderá assim que possível."
        ),
        color=0xffffff
    )

    embed.add_field(
        name="📌 Antes de abrir um ticket",
        value=(
            "• Descreva seu problema com detalhes.\n"
            "• Aguarde a resposta da equipe.\n"
            "• Evite abrir tickets duplicados.\n"
            "• Mantenha o respeito durante o atendimento."
        ),
        inline=False
    )

    embed.add_field(
        name="ℹ️ Informações",
        value=(
            "• Apenas você e a equipe terão acesso ao ticket.\n"
            "• O ticket será encerrado após a resolução.\n"
            "• Um ticket por usuário."
        ),
        inline=False
    )

    embed.set_thumbnail(
        url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None
    )

    if interaction.guild and interaction.guild.banner:
        embed.set_image(url=interaction.guild.banner.url)

    embed.set_footer(
        text=f"{interaction.guild.name} • Sistema de Tickets" if interaction.guild else "Sistema de Tickets"
    )

    # Send the panel with the ticket button
    await interaction.response.send_message(embed=embed, view=TicketView())
