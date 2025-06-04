import discord
from discord.ext import commands
import sqlite3
import os
import json
import math

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.getenv('DB_PATH', 'data/xp.db')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._load_config()

    def _create_tables(self):
        """Cria as tabelas no SQLite"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def _load_config(self):
        """Carrega configurações iniciais"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO config (key, value) 
            VALUES ('cargos_autorizados', '[]'), ('canal_logs', '1351205259091120190')
        ''')
        self.conn.commit()

    async def verificar_permissao(self, ctx):
        """Verifica se o usuário tem permissão"""
        if ctx.author.guild_permissions.administrator:
            return True
        self.cursor.execute('SELECT value FROM config WHERE key = "cargos_autorizados"')
        cargos_autorizados = json.loads(self.cursor.fetchone()[0])
        for cargo_id in cargos_autorizados:
            if cargo_id in [role.id for role in ctx.author.roles]:
                return True
        await ctx.send("❌ Você não tem permissão para usar este comando!")
        return False

    TABELA_NIVEIS = {
        1: 0, 2: 500, 3: 1200, 4: 2100, 5: 3700,
        6: 5500, 7: 7500, 8: 9600, 9: 12600,
        10: 15700, 11: 18900, 12: 22200, 13: 26000,
        14: 30300, 15: 34700
    }

    def calcular_nivel(self, xp):
        """Calcula o nível baseado na tabela"""
        for nivel, xp_necessario in sorted(self.TABELA_NIVEIS.items(), reverse=True):
            if xp >= xp_necessario:
                return nivel
        return 1

    @commands.command()
    async def ranking(self, ctx, page: int = 1):
        """Exibe o ranking de todos os usuários com XP, paginado e com botões."""
        per_page = 10
        offset = (page - 1) * per_page

        self.cursor.execute("SELECT user_id, xp FROM users ORDER BY xp DESC LIMIT ? OFFSET ?", (per_page, offset))
        users = self.cursor.fetchall()

        if not users:
            await ctx.send(f"📜 Não há usuários nesta página do ranking!")
            return

        total_users = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_pages = math.ceil(total_users / per_page)

        embed = discord.Embed(title=f"🏆 Ranking XP - Página {page}/{total_pages}", color=discord.Color.gold())

        for i, (user_id, xp) in enumerate(users, start=offset + 1):
            member = ctx.guild.get_member(user_id)
            if member:
                username = member.display_name
            else:
                try:
                    user_data = await self.bot.fetch_user(user_id)
                    username = user_data.name if user_data else f"Usuário desconhecido ({user_id})"
                except:
                    username = f"Usuário desconhecido ({user_id})"
            
            embed.add_field(name=f"#{i} {username}", value=f"XP: {xp}", inline=False)

        embed.set_footer(text="Use as setas ⬅️➡️ para navegar.")
        view = RankingView(self.bot, page)
        await ctx.send(embed=embed, view=view)

class RankingView(discord.ui.View):
    def __init__(self, bot, page=1):
        super().__init__()
        self.bot = bot
        self.page = page

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await XP.ranking(self.bot, interaction, page=self.page)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        await XP.ranking(self.bot, interaction, page=self.page)

async def setup(bot):
    await bot.add_cog(XP(bot))
