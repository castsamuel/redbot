import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import json
import os

# =========================================================
# CONFIG
# =========================================================

TOKEN = 

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

import time

# =========================================================
# EVENTO XP
# =========================================================

XP_CHANNEL = 1506087473351229592

mensagens_xp = 0

ultimo_evento = 0

COOLDOWN_EVENTO = 600
# 10 minutos

MENSAGENS_NECESSARIAS = 15

@bot.event
async def on_message(message):

    global mensagens_xp
    global ultimo_evento

    if message.author.bot:
        return

    # =====================================================
    # CHAT DO EVENTO
    # =====================================================

    if message.channel.id == XP_CHANNEL:

        agora = time.time()

        # =================================================
        # COOLDOWN
        # =================================================

        if agora - ultimo_evento >= COOLDOWN_EVENTO:

            mensagens_xp += 1

            # =============================================
            # ENVIA EVENTO
            # =============================================

            if mensagens_xp >= MENSAGENS_NECESSARIAS:

                mensagens_xp = 0

                ultimo_evento = agora

                embed = criar_embed(
                    f"{MARTELO} Evento de XP",
                    f"""
> <:emoji_7:1506459277517131868> . Nosso servidor está realizando um **Evento de XP** com prêmio de **R$ 25 em gift card**, à escolha do vencedor! 🎉

> <:blackstar:1507052823773450270> . Quanto mais XP você ganhar, maiores serão suas chances de vencer.

> <:red_line2:1506455266940551188> . Para conferir todas as informações, regras e detalhes do evento, clique [aqui](https://discord.com/channels/1506087472910565466/1506087472910565469/1507073321865445657).
"""
                )

                await message.channel.send(
                    embed=embed,
                    delete_after=10
                )

    await bot.process_commands(message)

# =========================================================
# PASTA
# =========================================================

BACKUP_FOLDER = "backups"

os.makedirs(
    BACKUP_FOLDER,
    exist_ok=True
)

# =========================================================
# EMBED
# =========================================================

def criar_embed(
    titulo,
    descricao
):

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
# CREATE BACKUP
# =========================================================

async def create_backup(
    guild: discord.Guild
):

    backup_id = str(
        int(time.time())
    )

    data = {

        "guild_name":
        guild.name,

        "roles":
        [],

        "categories":
        [],

        "channels":
        [],

        "members":
        [],

        "created_at":
        int(time.time())
    }

    # =====================================================
    # ROLES
    # =====================================================

    roles = sorted(
        guild.roles,
        key=lambda r: r.position
    )

    for role in roles:

        if role.is_default():
            continue

        data["roles"].append({

            "name":
            role.name,

            "permissions":
            role.permissions.value,

            "color":
            role.color.value,

            "hoist":
            role.hoist,

            "mentionable":
            role.mentionable,

            "position":
            role.position
        })

    # =====================================================
    # CATEGORIES
    # =====================================================

    for category in guild.categories:

        data["categories"].append({

            "name":
            category.name,

            "position":
            category.position
        })

    # =====================================================
    # CHANNELS
    # =====================================================

    for channel in guild.channels:

        channel_data = {

            "name":
            channel.name,

            "type":
            str(channel.type),

            "position":
            channel.position,

            "category":
            (
                channel.category.name
                if channel.category
                else None
            )
        }

        # =================================================
        # TEXT CHANNEL
        # =================================================

        if isinstance(
            channel,
            discord.TextChannel
        ):

            channel_data["topic"] = (
                channel.topic
            )

            channel_data["slowmode_delay"] = (
                channel.slowmode_delay
            )

            channel_data["nsfw"] = (
                channel.nsfw
            )

        # =================================================
        # VOICE CHANNEL
        # =================================================

        elif isinstance(
            channel,
            discord.VoiceChannel
        ):

            channel_data["bitrate"] = (
                channel.bitrate
            )

            channel_data["user_limit"] = (
                channel.user_limit
            )

        data["channels"].append(
            channel_data
        )

    # =====================================================
    # MEMBERS
    # =====================================================

    for member in guild.members:

        roles = [

            r.name

            for r in member.roles

            if not r.is_default()
        ]

        data["members"].append({

            "id":
            member.id,

            "roles":
            roles
        })

    # =====================================================
    # SAVE
    # =====================================================

    path = (
        f"{BACKUP_FOLDER}/"
        f"{backup_id}.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    return backup_id, path

# =========================================================
# LOAD BACKUP
# =========================================================

async def load_backup(
    guild: discord.Guild,
    backup_id: str
):

    path = (
        f"{BACKUP_FOLDER}/"
        f"{backup_id}.json"
    )

    # =====================================================
    # EXISTE?
    # =====================================================

    if not os.path.exists(path):
        return False

    # =====================================================
    # LOAD JSON
    # =====================================================

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # =====================================================
    # DELETE CHANNELS
    # =====================================================

    for channel in guild.channels:

        try:

            await channel.delete()

            await asyncio.sleep(0.7)

        except:
            pass

    # =====================================================
    # DELETE ROLES
    # =====================================================

    for role in guild.roles:

        if role.is_default():
            continue

        try:

            await role.delete()

            await asyncio.sleep(0.7)

        except:
            pass

    # =====================================================
    # CREATE ROLES
    # =====================================================

    created_roles = {}

    sorted_roles = sorted(
        data["roles"],
        key=lambda r: r["position"]
    )

    for role_data in sorted_roles:

        try:

            role = await guild.create_role(

                name=role_data["name"],

                permissions=discord.Permissions(
                    role_data["permissions"]
                ),

                colour=discord.Colour(
                    role_data["color"]
                ),

                hoist=role_data["hoist"],

                mentionable=role_data[
                    "mentionable"
                ]
            )

            created_roles[
                role.name
            ] = role

            await asyncio.sleep(0.7)

        except:
            pass

    # =====================================================
    # CREATE CATEGORIES
    # =====================================================

    created_categories = {}

    for category_data in data["categories"]:

        try:

            category = await guild.create_category(

                name=category_data["name"]
            )

            created_categories[
                category.name
            ] = category

            await asyncio.sleep(0.7)

        except:
            pass

    # =====================================================
    # CREATE CHANNELS
    # =====================================================

    for channel_data in data["channels"]:

        try:

            category = None

            if channel_data["category"]:

                category = created_categories.get(
                    channel_data["category"]
                )

            # =============================================
            # TEXT CHANNEL
            # =============================================

            if channel_data["type"] == "text":

                await guild.create_text_channel(

                    name=channel_data["name"],

                    category=category,

                    topic=channel_data.get(
                        "topic"
                    ),

                    slowmode_delay=channel_data.get(
                        "slowmode_delay",
                        0
                    ),

                    nsfw=channel_data.get(
                        "nsfw",
                        False
                    )
                )

            # =============================================
            # VOICE CHANNEL
            # =============================================

            elif channel_data["type"] == "voice":

                await guild.create_voice_channel(

                    name=channel_data["name"],

                    category=category,

                    bitrate=channel_data.get(
                        "bitrate",
                        64000
                    ),

                    user_limit=channel_data.get(
                        "user_limit",
                        0
                    )
                )

            await asyncio.sleep(0.7)

        except:
            pass

    # =====================================================
    # RESTORE MEMBER ROLES
    # =====================================================

    for member_data in data["members"]:

        member = guild.get_member(
            member_data["id"]
        )

        if not member:
            continue

        roles_to_add = []

        for role_name in member_data["roles"]:

            role = created_roles.get(
                role_name
            )

            if role:
                roles_to_add.append(
                    role
                )

        try:

            await member.add_roles(
                *roles_to_add
            )

            await asyncio.sleep(0.5)

        except:
            pass

    return True

# =========================================================
# AUTO BACKUP 12H
# =========================================================

@tasks.loop(hours=12)
async def auto_backup():

    canal = bot.get_channel(
        BACKUP_CHANNEL
    )

    if not canal:
        return

    guild = bot.get_guild(
        GUILD_ID
    )

    if not guild:
        return

    try:

        backup_id, path = await create_backup(
            guild
        )

        embed = criar_embed(
            f"{FANTASMA} Backup Automático",
            f"""
{MEMBRO} Servidor: {guild.name}

{FANTASMA} Backup ID: `{backup_id}`

{MARTELO} Backup automático realizado.
"""
        )

        await canal.send(

            embed=embed,

            file=discord.File(
                path,
                filename=f"{backup_id}.json"
            )
        )

    except Exception as e:

        print(
            f"ERRO BACKUP: {e}"
        )

# =========================================================
# BACKUP LOAD
# =========================================================

@bot.tree.command(
    name="backup_load",
    description="Restaura um backup.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    backup_id="ID do backup"
)
async def backup_load(
    interaction: discord.Interaction,
    backup_id: str
):

    # =====================================================
    # PERMISSÃO
    # =====================================================

    if interaction.user.id not in [
        OWNER_ID,
        CO_OWNER_ID
    ]:

        embed = criar_embed(
            f"{CRUZ} Acesso Negado",
            f"{CRUZ} Você não possui permissão."
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # INÍCIO
    # =====================================================

    await interaction.response.send_message(
        embed=criar_embed(
            f"{FANTASMA} Restauração Iniciada",
            f"{CRUZ} O servidor será reconstruído."
        )
    )

    # =====================================================
    # RESTORE
    # =====================================================

    success = await load_backup(
        interaction.guild,
        backup_id
    )

    # =====================================================
    # RESULTADO
    # =====================================================

    if success:

        await interaction.followup.send(
            embed=criar_embed(
                f"{MARTELO} Backup Restaurado",
                f"{MARTELO} O backup foi restaurado com sucesso."
            )
        )

    else:

        await interaction.followup.send(
            embed=criar_embed(
                f"{CRUZ} Erro",
                f"{CRUZ} Backup não encontrado."
            )
        )
# =========================================================
# RUN
# =========================================================

bot.run(TOKEN)
