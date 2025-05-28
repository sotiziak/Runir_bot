from discord.ext import commands
import random
import re

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='r', aliases=['roll'])
    async def rolar(self, ctx, *, expressao: str = "d20"):
        """Rola dados (formato: [X]dY±Z ou dY±Z)"""
        try:
            expressao = expressao.replace(" ", "").lower()
            if expressao.startswith('d'):
                expressao = '1' + expressao

            if not re.match(r'^(\d*d\d+([k|kl]\d+)?([*/+-]\d*d\d+|[*/+-]\d+)*)$', expressao):
                await ctx.send("❌ Formato inválido! Exemplos:\n`-r d20`\n`-r d20+3`\n`-r 2d20k1`")
                return

            total = 0
            componentes = []
            partes = re.findall(r'\d*d\d+|[*/+-]\d+', expressao)  

            operador = '+'
            for parte in partes:
            if parte in '+-*/':
            operador = parte
            continue
            if 'd' in parte:  # Dice roll
            qtd, faces = map(int, parte.split('d'))
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

        componentes.append(f"🎯 {texto}\n`{' '.join(map(str, resultados))}` = `{subtotal}`")
    else:  # Modifier
        valor = int(parte)
        total = eval(f"{total}{operador}{valor}")
        componentes.append(f"📝 Modificador `{operador}{valor}`")
                    total += valor if operador == '+' else -valor

            resposta = [
                f"{ctx.author.mention} rolou:",
                f"🎲 `{expressao}`",
                *componentes,
                f"**Total:** `{total}`"
            ]

            if 'd20' in expressao.lower():
                resultados_verificacao = selecionados if isinstance(selecionados, list) else [selecionados]
                if 20 in resultados_verificacao:
                    resposta.append("💥 **Crítico!**")
                if 1 in resultados_verificacao:
                    resposta.append("💀 **Falha!**")
            await ctx.send('\n'.join(resposta))

        except Exception as e:
            await ctx.send(f"❌ Erro: {e}\n💡 Use: `-r 2d20k1+3`")

async def setup(bot):
    await bot.add_cog(Dados(bot))
