import discord
from discord import app_commands

class Trinity(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"O Bot {self.user} foi ligado com sucesso.")

    async def on_member_join(self, member: discord.Member):
        canal = self.get_channel(1519885555603865723)

        if canal is None:
            return

        embed = discord.Embed(
            title="🎉 Bem-vindo(a)!",
            description="Antes de tudo leia o canal <#1519885555603865727>!",
            color=0x5865F2
        )

        embed.set_author(
            name=str(member),
            icon_url=member.display_avatar.url
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_image(
            url="https://raw.githubusercontent.com/deerriene/trinity-assets/main/3wEKy.jpg"
        )

        embed.add_field(
            name="👥 Membros",
            value=f"{member.guild.member_count}",
            inline=True
        )

        embed.set_footer(
            text=f"ID: {member.id}"
        )

        await canal.send(
            content=f"🎉 {member.mention} entrou para **TRINITY**!",
            embed=embed
        )

bot = Trinity()

@bot.tree.command(name="olá-mundo",description="Primeiro comando do Bot")
async def olamundo(interaction:discord.Interaction):
    await interaction.response.send_message(f"Olá {interaction.user.mention}!")

@bot.tree.command(name="soma",description="Some dois números distintos")
@app_commands.describe(
    numero1="Primeiro numero a somar",
    numero2="Segundo número a somar"
)
async def olamundo(interaction:discord.Interaction,numero1:int,numero2:int):
    numero_somado = numero1 + numero2
    await interaction.response.send_message(f"O numero somado é {numero_somado}.",ephemeral=True)

import os
bot.run(os.getenv("DISCORD_TOKEN"))
