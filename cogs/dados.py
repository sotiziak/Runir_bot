from discord.ext import commands
import random
import re

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='r', aliases=['roll'])
    async def rolar(self, ctx, *, expressao: str = "d20"):
        """Rola dados (formato: [X]dY±Z ou dY±Z, suporta múltiplos dados e operações matemáticas)"""
        try:
            expressao = expressao.replace(" ", "").lower()
            if expressao.startswith('d'):
                expressao = '1' + expressao  

            if not re.match(r'^(\d*d\d+([k|kl]\d+)?([*/+-]\d*d\d+|[*/+-]\d+)*)$', expressao):
                await ctx.send("❌ Formato inválido! Exemplos:\n`-r d20`\n`-r 2d20+3`\n`-r 1d10+1d4`\n`-r 2d6*2`")
                return

            total = 0
            componentes = []
            partes = re.findall(r'\d*d\d+|[*/+-]\d+', expressao) 
            operador = '+'

            for parte in partes:
                if parte in '+-*/':
                    operador = parte
                    continue

                if 'd' in parte: 
                    qtd, faces = map(int, parte.split('d')) if 'd' in parte else (1, int(parte))
                    resultados = [random.randint(1, faces) for _ in range(qtd)]
                    subtotal = sum(resultados)
                    texto = f"{qtd}d{faces}"

                    if operador == '*':
                        total *= subtotal
                    elif operador == '/':
                        total /= subtotal
                    elif operador == '-':
                        total -= subtotal
                    else:
                        total += subtotal

                    componentes.append(f"🎲 {texto} → `{resultados}` → **{subtotal}**")

                else:  
                    valor = int(parte)
                    total = eval(f"{total}{operador}{valor}")
                    componentes.append(f"📝 Modificador `{operador}{valor}`")

            resposta = [
                f"{ctx.author.mention} rolou:",
                f"🎲 `{expressao}`",
                *componentes,
                f"**Total:** `{total}`"
            ]

            if 'd20' in expressao.lower():
                if 20 in resultados:
                    resposta.append("💥 **Crítico!**")
                if 1 in resultados:
                    resposta.append("💀 **Falha!**")

            await ctx.send('\n'.join(resposta))

        except Exception as e:
            await ctx.send(f"❌ Erro: {e}\n💡 Use: `-r 2d20k1+3`")

async def setup(bot):
    await bot.add_cog(Dados(bot))
