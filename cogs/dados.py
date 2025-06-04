from discord.ext import commands
import random
import re

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def processar_dados(self, expressao):
        """Processa rolagens como '1d10+1d4' corretamente"""
        partes = re.findall(r'(\d*)d(\d+)', expressao)  # Captura todas rolagens de dados
        resultados = []

        for quantidade, faces in partes:
            quantidade = int(quantidade) if quantidade else 1  # Assume "d20" como "1d20"
            faces = int(faces)
            valores_rolados = [random.randint(1, faces) for _ in range(quantidade)]
            resultados.append((f"{quantidade}d{faces}", valores_rolados, sum(valores_rolados)))

        return resultados

    @commands.command(name='r', aliases=['roll'])
    async def rolar(self, ctx, *, expressao: str = "d20"):
        """Rola dados (exemplo: '2d20+3', '1d10+1d4', '2d6*2')"""
        try:
            expressao = expressao.replace(" ", "").lower()
            if expressao.startswith('d'):
                expressao = '1' + expressao  

            if not re.match(r'^(\d*d\d+([*/+-]\d*d\d+|[*/+-]\d+)*)$', expressao):
                await ctx.send("❌ Formato inválido! Exemplos:\n`-r d20`\n`-r 2d20+3`\n`-r 1d10+1d4`\n`-r 2d6*2`")
                return

            total = 0
            componentes = []
            operador = '+'
            dados_rolados = self.processar_dados(expressao)
            
            for texto, valores, subtotal in dados_rolados:
                componentes.append(f"🎲 {texto} → `{valores}` → **{subtotal}**")
                total += subtotal

            modificadores = re.findall(r'([*/+-]\d+)', expressao)
            for mod in modificadores:
                total = eval(f"{total}{mod}")
                componentes.append(f"📝 Modificador `{mod}`")

            resposta = [
                f"{ctx.author.mention} rolou:",
                f"🎲 `{expressao}`",
                *componentes,
                f"**Total:** `{total}`"
            ]

            if 'd20' in expressao.lower():
                if 20 in valores:
                    resposta.append("💥 **Crítico!**")
                if 1 in valores:
                    resposta.append("💀 **Falha!**")

            await ctx.send('\n'.join(resposta))

        except Exception as e:
            await ctx.send(f"❌ Erro: {e}\n💡 Use: `-r 2d20+3`")

async def setup(bot):
    await bot.add_cog(Dados(bot))
