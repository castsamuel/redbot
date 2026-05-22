import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import json
import os

# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1506087472910565466

PUNISHMENT_CHANNEL = 1507062463022239924

OWNER_ID = 1463615541657731183
CO_OWNER_ID = 1502699917800640693

COLOR = 0x5A0000

# =========================================================
# EMOJIS
# =========================================================

CRUZ = "<:emoji_7:1506459277517131868>"
MARTELO = "<:3978staff:1507053183279824896>"
MUTE = "<:1253muted:1507053047711268894>"
MEMBRO = "<:7188members:1507053387554881698>"
LINHA = "<:red_line2:1506455266940551188>"
FANTASMA = "<:emoji_5:1506459131060686848>"

# =========================================================
# BOT
# =========================================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================================================
# JSON
# =========================================================

ARQUIVOS = {
    "warns": "warns.json",
    "mutes": "mutes.json",
    "allowed_bots": "allowed_bots.json"
}

def carregar_json(nome):

    if not os.path.exists(ARQUIVOS[nome]):

        with open(ARQUIVOS[nome], "w") as f:
            json.dump({}, f)

    with open(ARQUIVOS[nome], "r") as f:
        return json.load(f)

def salvar_json(nome, dados):

    with open(ARQUIVOS[nome], "w") as f:
        json.dump(dados, f, indent=4)

warns_data = carregar_json("warns")
mutes_data = carregar_json("mutes")
allowed_bots = carregar_json("allowed_bots")

# =========================================================
# EMBED
# =========================================================

def criar_embed(titulo, descricao):

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=COLOR
    )

    embed.set_footer(
        text="Red's Assistant"
    )

    return embed

# =========================================================
# DM
# =========================================================

async def enviar_dm(usuario, embed):

    try:
        await usuario.send(embed=embed)

    except Exception as e:
        print(f"ERRO DM: {e}")

# =========================================================
# VERIFICAR PERMISSÃO
# =========================================================

async def verificar_permissao(interaction, usuario):

    if usuario.bot:

        embed = criar_embed(
            f"{CRUZ} Ação Negada",
            f"""
{CRUZ} Você não pode punir bots.
"""
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return False

    if usuario == interaction.user:

        embed = criar_embed(
            f"{CRUZ} Ação Negada",
            f"""
{CRUZ} Você não pode punir a si mesmo.
"""
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return False

    if usuario == interaction.guild.owner:

        embed = criar_embed(
            f"{CRUZ} Ação Negada",
            f"""
{CRUZ} Você não pode punir o dono do servidor.
"""
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return False

    if usuario.top_role >= interaction.user.top_role:

        embed = criar_embed(
            f"{CRUZ} Ação Negada",
            f"""
{CRUZ} Você não possui permissão para punir este usuário.

{LINHA} Verifique a hierarquia de cargos.
"""
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return False

    if usuario.top_role >= interaction.guild.me.top_role:

        embed = criar_embed(
            f"{CRUZ} Ação Negada",
            f"""
{CRUZ} Meu cargo está abaixo do usuário.

{LINHA} Mova meu cargo para cima.
"""
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return False

    return True

# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    try:

        guild = discord.Object(id=GUILD_ID)

        bot.tree.clear_commands(guild=guild)

        synced = await bot.tree.sync(guild=guild)

        print(f"{len(synced)} comandos sincronizados.")

    except Exception as e:

        print(f"ERRO SYNC: {e}")

    print(f"{bot.user} online!")

# =========================================================
# ANTI RAID
# =========================================================

@bot.event
async def on_member_join(member):

    if not member.bot:
        return

    if str(member.id) in allowed_bots:
        return

    adicionou = None

    async for entry in member.guild.audit_logs(
        limit=1,
        action=discord.AuditLogAction.bot_add
    ):

        if entry.target.id == member.id and entry.user:

            adicionou = entry.user
            break

    try:

        await member.kick(reason="Anti Raid")

    except Exception as e:
        print(e)
        return

    embed = criar_embed(
        f"{FANTASMA} Anti Raid",
        f"""
{MEMBRO} Bot: {member.mention}

{MARTELO} Adicionado por: {adicionou.mention if adicionou else 'Desconhecido'}

{CRUZ} Ação: Expulsão automática
"""
    )

    canal = bot.get_channel(PUNISHMENT_CHANNEL)

    if canal:
        await canal.send(embed=embed)

    try:

        dono = await bot.fetch_user(OWNER_ID)

        await dono.send(embed=embed)

    except Exception as e:
        print(e)

# =========================================================
# LIBERAR BOT
# =========================================================

@bot.tree.command(
    name="liberarbot",
    description="Autoriza um bot no anti raid."
)
async def liberarbot(
    interaction: discord.Interaction,
    bot_id: str
):

    if interaction.user.id not in [OWNER_ID, CO_OWNER_ID]:

        embed = criar_embed(
            f"{CRUZ} Acesso Negado",
            f"{CRUZ} Você não possui permissão."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    allowed_bots[str(bot_id)] = True

    salvar_json("allowed_bots", allowed_bots)

    embed = criar_embed(
        f"{FANTASMA} Bot Liberado",
        f"""
{FANTASMA} ID autorizado: `{bot_id}`
"""
    )

    await interaction.response.send_message(embed=embed)

# =========================================================
# DESLIBERAR BOT
# =========================================================

@bot.tree.command(
    name="desliberar",
    description="Remove um bot da whitelist."
)
async def desliberar(
    interaction: discord.Interaction,
    bot_id: str
):

    if interaction.user.id not in [OWNER_ID, CO_OWNER_ID]:

        embed = criar_embed(
            f"{CRUZ} Acesso Negado",
            f"{CRUZ} Você não possui permissão."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    if bot_id not in allowed_bots:

        embed = criar_embed(
            f"{CRUZ} Erro",
            f"{CRUZ} Este bot não está liberado."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    del allowed_bots[bot_id]

    salvar_json("allowed_bots", allowed_bots)

    embed = criar_embed(
        f"{FANTASMA} Bot Desautorizado",
        f"""
{MARTELO} Responsável: {interaction.user.mention}

{FANTASMA} ID removido: `{bot_id}`

{CRUZ} O anti raid voltará a agir normalmente.
"""
    )

    await interaction.response.send_message(embed=embed)

# =========================================================
# BOTS LIBERADOS
# =========================================================

@bot.tree.command(
    name="botsliberados",
    description="Mostra os bots liberados."
)
async def botsliberados(
    interaction: discord.Interaction
):

    if interaction.user.id not in [OWNER_ID, CO_OWNER_ID]:

        embed = criar_embed(
            f"{CRUZ} Acesso Negado",
            f"{CRUZ} Você não possui permissão."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    if not allowed_bots:

        embed = criar_embed(
            f"{FANTASMA} Bots Liberados",
            f"{CRUZ} Nenhum bot está liberado."
        )

        return await interaction.response.send_message(embed=embed)

    descricao = ""

    for bot_id in allowed_bots:

        try:

            usuario = await bot.fetch_user(int(bot_id))

            descricao += f"{LINHA} {usuario} (`{bot_id}`)\n"

        except:

            descricao += f"{LINHA} ID desconhecido (`{bot_id}`)\n"

    embed = criar_embed(
        f"{FANTASMA} Bots Liberados",
        descricao
    )

    await interaction.response.send_message(embed=embed)

# =========================================================
# WARN
# =========================================================

@bot.tree.command(
    name="warn",
    description="Aplica uma advertência."
)
@app_commands.default_permissions(
    moderate_members=True
)
async def warn(
    interaction: discord.Interaction,
    usuario: discord.Member,
    motivo: str = "Sem motivo"
):

    if not await verificar_permissao(interaction, usuario):
        return

    user_id = str(usuario.id)

    if user_id not in warns_data:
        warns_data[user_id] = []

    warns_data[user_id].append({
        "staff": interaction.user.id,
        "motivo": motivo
    })

    salvar_json("warns", warns_data)

    embed = criar_embed(
        f"{MARTELO} Advertência Aplicada",
        f"""
{MARTELO} Punido por: {interaction.user.mention}

{MEMBRO} Punido: {usuario.mention}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: {motivo}
"""
    )

    await interaction.response.send_message(embed=embed)

    canal = bot.get_channel(PUNISHMENT_CHANNEL)

    if canal:
        await canal.send(embed=embed)

    dm_embed = criar_embed(
        f"{MARTELO} Você Recebeu Uma Advertência",
        f"""
{MARTELO} Staff: {interaction.user}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: {motivo}
"""
    )

    await enviar_dm(usuario, dm_embed)

    if len(warns_data[user_id]) >= 3:

        dm_ban = criar_embed(
            f"{MARTELO} Você Foi Banido",
            f"""
{LINHA} Tempo: Permanente

{CRUZ} Motivo: Alcançou 3 advertências
"""
        )

        await enviar_dm(usuario, dm_ban)

        await usuario.ban(
            reason="Alcançou 3 advertências"
        )

        warns_data[user_id] = []

        salvar_json("warns", warns_data)

        auto_ban = criar_embed(
            f"{MARTELO} Banimento Automático",
            f"""
{MARTELO} Punido por: {bot.user.mention}

{MEMBRO} Punido: {usuario.mention}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: Alcançou 3 advertências
"""
        )

        if canal:
            await canal.send(embed=auto_ban)

# =========================================================
# MUTE
# =========================================================

@bot.tree.command(
    name="mute",
    description="Silencia um usuário."
)
@app_commands.default_permissions(
    moderate_members=True
)
async def mute(
    interaction: discord.Interaction,
    usuario: discord.Member,
    tempo: int,
    motivo: str = "Sem motivo"
):

    if not await verificar_permissao(interaction, usuario):
        return

    await usuario.timeout(
        timedelta(minutes=tempo),
        reason=motivo
    )

    user_id = str(usuario.id)

    if user_id not in mutes_data:
        mutes_data[user_id] = []

    mutes_data[user_id].append({
        "staff": interaction.user.id,
        "motivo": motivo,
        "tempo": tempo
    })

    salvar_json("mutes", mutes_data)

    embed = criar_embed(
        f"{MUTE} Silenciamento Aplicado",
        f"""
{MARTELO} Punido por: {interaction.user.mention}

{MEMBRO} Punido: {usuario.mention}

{MUTE} Tempo: {tempo} minuto(s)

{CRUZ} Motivo: {motivo}
"""
    )

    await interaction.response.send_message(embed=embed)

    canal = bot.get_channel(PUNISHMENT_CHANNEL)

    if canal:
        await canal.send(embed=embed)

    dm_embed = criar_embed(
        f"{MUTE} Você Foi Silenciado",
        f"""
{MARTELO} Staff: {interaction.user}

{MUTE} Tempo: {tempo} minuto(s)

{CRUZ} Motivo: {motivo}
"""
    )

    await enviar_dm(usuario, dm_embed)

    if len(mutes_data[user_id]) >= 3:

        mutes_data[user_id] = []

        salvar_json("mutes", mutes_data)

        if user_id not in warns_data:
            warns_data[user_id] = []

        warns_data[user_id].append({
            "staff": bot.user.id,
            "motivo": "Alcançou 3 silenciamentos"
        })

        salvar_json("warns", warns_data)

        auto_warn = criar_embed(
            f"{MARTELO} Advertência Automática",
            f"""
{MARTELO} Punido por: {bot.user.mention}

{MEMBRO} Punido: {usuario.mention}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: Alcançou 3 silenciamentos
"""
        )

        if canal:
            await canal.send(embed=auto_warn)

        dm_warn = criar_embed(
            f"{MARTELO} Advertência Automática",
            f"""
{LINHA} Tempo: Permanente

{CRUZ} Motivo: Alcançou 3 silenciamentos
"""
        )

        await enviar_dm(usuario, dm_warn)

        if len(warns_data[user_id]) >= 3:

            dm_ban = criar_embed(
                f"{MARTELO} Você Foi Banido",
                f"""
{LINHA} Tempo: Permanente

{CRUZ} Motivo: Alcançou 3 advertências
"""
            )

            await enviar_dm(usuario, dm_ban)

            await usuario.ban(
                reason="Alcançou 3 advertências"
            )

            warns_data[user_id] = []

            salvar_json("warns", warns_data)

            auto_ban = criar_embed(
                f"{MARTELO} Banimento Automático",
                f"""
{MARTELO} Punido por: {bot.user.mention}

{MEMBRO} Punido: {usuario.mention}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: Alcançou 3 advertências
"""
            )

            if canal:
                await canal.send(embed=auto_ban)

# =========================================================
# UNMUTE
# =========================================================

@bot.tree.command(
    name="unmute",
    description="Remove o silenciamento."
)
@app_commands.default_permissions(
    moderate_members=True
)
async def unmute(
    interaction: discord.Interaction,
    usuario: discord.Member
):

    if not await verificar_permissao(interaction, usuario):
        return

    await usuario.timeout(None)

    embed = criar_embed(
        f"{MUTE} Silenciamento Removido",
        f"""
{MARTELO} Responsável: {interaction.user.mention}

{MEMBRO} Usuário: {usuario.mention}

{LINHA} Tempo: Removido

{CRUZ} Motivo: Dessilenciamento
"""
    )

    await interaction.response.send_message(embed=embed)

    canal = bot.get_channel(PUNISHMENT_CHANNEL)

    if canal:
        await canal.send(embed=embed)

    dm_embed = criar_embed(
        f"{MUTE} Você Foi Dessilenciado",
        f"""
{MARTELO} Staff: {interaction.user}

{CRUZ} Seu silenciamento foi removido.
"""
    )

    await enviar_dm(usuario, dm_embed)

# =========================================================
# HISTÓRICO
# =========================================================

@bot.tree.command(
    name="historico",
    description="Mostra o histórico do usuário."
)
@app_commands.default_permissions(
    moderate_members=True
)
async def historico(
    interaction: discord.Interaction,
    usuario: discord.Member
):

    user_id = str(usuario.id)

    warns = warns_data.get(user_id, [])
    mutes = mutes_data.get(user_id, [])

    descricao = f"""
{MEMBRO} Usuário: {usuario.mention}

{MARTELO} Advertências: {len(warns)}

{MUTE} Silenciamentos: {len(mutes)}
"""

    if warns:

        descricao += f"\n{MARTELO} Warns:\n"

        for warn_data in warns:

            descricao += f"{LINHA} {warn_data['motivo']}\n"

    if mutes:

        descricao += f"\n{MUTE} Mutes:\n"

        for mute_data in mutes:

            descricao += f"{LINHA} {mute_data['motivo']} ({mute_data['tempo']} min)\n"

    embed = criar_embed(
        f"{MEMBRO} Histórico",
        descricao
    )

    await interaction.response.send_message(embed=embed)

# =========================================================
# BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Bane um usuário."
)
@app_commands.default_permissions(
    ban_members=True
)
async def ban(
    interaction: discord.Interaction,
    usuario: discord.Member,
    motivo: str = "Sem motivo"
):

    if not await verificar_permissao(interaction, usuario):
        return

    dm_embed = criar_embed(
        f"{MARTELO} Você Foi Banido",
        f"""
{MARTELO} Staff: {interaction.user}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: {motivo}
"""
    )

    await enviar_dm(usuario, dm_embed)

    await usuario.ban(
        reason=motivo
    )

    embed = criar_embed(
        f"{MARTELO} Banimento Aplicado",
        f"""
{MARTELO} Punido por: {interaction.user.mention}

{MEMBRO} Punido: {usuario.mention}

{LINHA} Tempo: Permanente

{CRUZ} Motivo: {motivo}
"""
    )

    await interaction.response.send_message(embed=embed)

    canal = bot.get_channel(PUNISHMENT_CHANNEL)

    if canal:
        await canal.send(embed=embed)

# =========================================================
# UNBAN
# =========================================================

@bot.tree.command(
    name="unban",
    description="Remove o banimento."
)
@app_commands.default_permissions(
    ban_members=True
)
async def unban(
    interaction: discord.Interaction,
    usuario_id: str
):

    try:

        usuario = await bot.fetch_user(int(usuario_id))

    except:

        embed = criar_embed(
            f"{CRUZ} Erro",
            f"{CRUZ} Usuário não encontrado."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    try:

        await interaction.guild.unban(usuario)

    except:

        embed = criar_embed(
            f"{CRUZ} Erro",
            f"{CRUZ} Este usuário não está banido."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    embed = criar_embed(
        f"{MARTELO} Banimento Removido",
        f"""
{MARTELO} Responsável: {interaction.user.mention}

{MEMBRO} Usuário: {usuario.mention}

{LINHA} Tempo: Removido

{CRUZ} Motivo: Desbanimento
"""
    )

    await interaction.response.send_message(embed=embed)

    canal = bot.get_channel(PUNISHMENT_CHANNEL)

    if canal:
        await canal.send(embed=embed)

    dm_embed = criar_embed(
        f"{MARTELO} Você Foi Desbanido",
        f"""
{MARTELO} Staff: {interaction.user}

{CRUZ} Seu banimento foi removido.
"""
    )

    await enviar_dm(usuario, dm_embed)

# =========================================================
# RUN
# =========================================================

bot.run(TOKEN)
