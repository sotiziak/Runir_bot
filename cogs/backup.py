import discord
from discord.ext import commands, tasks
import os
import shutil
from datetime import datetime

class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'data/xp.db'
        self.backup_dir = 'backups'
        os.makedirs(self.backup_dir, exist_ok=True)
        self.backup_periodico.start()

    def cog_unload(self):
        self.backup_periodico.cancel()

    def criar_backup(self):
        if not os.path.exists(self.db_path):
            return None
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_path = os.path.join(self.backup_dir, f'xp_backup_{timestamp}.db')
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    @tasks.loop(hours=6)
    async def backup_periodico(self):
        self.criar_backup()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        """Cria um backup manualmente"""
        caminho = self.criar_backup()
        if caminho:
            await ctx.send(f"✅ Backup criado: `{os.path.basename(caminho)}`")
        else:
            await ctx.send("❌ Banco de dados não encontrado.")

async def setup(bot):
    await bot.add_cog(Backup(bot))
