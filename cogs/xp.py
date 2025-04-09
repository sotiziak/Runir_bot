import discord
from discord.ext import commands
import sqlite3
import os
import json

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
    async def xp(self, ctx, usuario: discord.Member = None):
        """Mostra XP e nível"""
        alvo = usuario or ctx.author
        self.cursor.execute('SELECT xp FROM users WHERE user_id = ?', (alvo.id,))
        resultado = self.cursor.fetchone()
        xp = resultado[0] if resultado else 0
        nivel = self.calcular_nivel(xp)
        xp_proximo = self.TABELA_NIVEIS.get(nivel + 1, 0)
        progresso = xp - self.TABELA_NIVEIS[nivel]
        necessario = xp_proximo - self.TABELA_NIVEIS[nivel] if nivel < 15 else 0

        embed = discord.Embed(title=f"🏆 Nível {nivel} | {alvo.display_name}", color=0x00ff00)
        embed.add_field(name="XP Total", value=f"`{xp}`", inline=True)
        if nivel < 15:
            embed.add_field(name="Próximo Nível", value=f"`{xp_proximo} XP`", inline=True)
            embed.add_field(name="Progresso", value=f"`{progresso}/{necessario}` ({progresso/necessario:.0%})", inline=False)
        else:
            embed.add_field(name="🎯 Status", value="Nível Máximo Alcançado!", inline=True)
        embed.set_thumbnail(url=alvo.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def ranking(self, ctx):
        """Mostra o top 10 de XP"""
        self.cursor.execute('SELECT user_id, xp FROM users ORDER BY xp DESC LIMIT 10')
        ranking = self.cursor.fetchall()
        embed = discord.Embed(title="🏅 Ranking de XP", color=0xffd700)
        for posicao, (user_id, xp) in enumerate(ranking, start=1):
            user = await self.bot.fetch_user(user_id)
            nivel = self.calcular_nivel(xp)
            embed.add_field(
                name=f"{posicao}º - {user.display_name}",
                value=f"`Nível {nivel} | {xp} XP`",
                inline=False
            )
        if not embed.fields:
            embed.description = "Ninguém possui XP registrado ainda!"
        await ctx.send(embed=embed)

    @commands.command()
    async def xpadd(self, ctx, usuario: discord.Member, quantidade: int):
        """Adiciona XP"""
        if not await self.verificar_permissao(ctx):
            return
        self.cursor.execute('''
            INSERT INTO users (user_id, xp) 
            VALUES (?, COALESCE((SELECT xp FROM users WHERE user_id = ?), 0) + ?)
            ON CONFLICT(user_id) DO UPDATE SET xp = xp + ?
        ''', (usuario.id, usuario.id, quantidade, quantidade))
        self.conn.commit()
        nivel_antigo = self.calcular_nivel(self.cursor.execute('SELECT xp FROM users WHERE user_id = ?', (usuario.id,)).fetchone()[0] - quantidade)
        nivel_novo = self.calcular_nivel(self.cursor.execute('SELECT xp FROM users WHERE user_id = ?', (usuario.id,)).fetchone()[0])
        await ctx.send(f"✅ {quantidade} XP adicionados para {usuario.mention}")
        if nivel_novo > nivel_antigo:
            await ctx.send(f"🎉 {usuario.mention} subiu para o nível {nivel_novo}!")

    @commands.command()
    async def xpremove(self, ctx, usuario: discord.Member, quantidade: int):
        """Remove XP"""
        if not await self.verificar_permissao(ctx):
            return
        self.cursor.execute('''
            UPDATE users SET xp = MAX(0, xp - ?) WHERE user_id = ?
        ''', (quantidade, usuario.id))
        self.conn.commit()
        await ctx.send(f"✅ {quantidade} XP removidos de {usuario.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def xpreset(self, ctx, usuario: discord.Member):
        """Reseta XP"""
        self.cursor.execute('DELETE FROM users WHERE user_id = ?', (usuario.id,))
        self.conn.commit()
        await ctx.send(f"✅ XP de {usuario.mention} foi resetado!")

async def setup(bot):
    await bot.add_cog(XP(bot))
