import discord
from discord.ext import commands
import os
from dotenv import load_dotenv  # Adicione esta linha
import asyncio

# Carrega variáveis do .env
load_dotenv()  # Adicione esta linha

# Configurações
TOKEN = os.getenv('DISCORD_TOKEN')  # Alterado para os.getenv()
PREFIXO = os.getenv('PREFIXO', '-')  # Prefixo padrão caso não exista
GUILD_ID = int(os.getenv('GUILD_ID', 0))  # ID do servidor

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIXO, intents=intents)

async def load_cogs():
    """Carrega todos os módulos da pasta cogs"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ Cog carregada: {filename}')
            except Exception as e:
                print(f'❌ Falha ao carregar {filename}: {e}')

@bot.event
async def on_ready():
    """Evento de inicialização do bot"""
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    print(f'✅ Conectado ao servidor: {guild.name} (ID: {guild.id})')
    print(f'🤖 Bot conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name=f"{PREFIXO}ajuda"))

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Sincroniza comandos slash (apenas dono)"""
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await ctx.send("✅ Comandos sincronizados!")

@bot.command()
@commands.is_owner()
async def reload(ctx):
    """Recarrega todos os módulos"""
    for cog in list(bot.extensions):
        await bot.reload_extension(cog)
    await ctx.send("✅ Todos os módulos recarregados!")

@bot.command()
async def ping(ctx):
    """Verifica a latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())