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

            if not re.match(r'^(\d+d\d+(k|kl)\d+|\d+d\d+|[+-]?\d+)+$', expressao):
                await ctx.send("❌ Formato inválido! Exemplos:\n`!r d20`\n`!r d20+3`\n`!r 2d20k1`")
                return

            total = 0
            componentes = []
            partes = re.split(r'([+-])', expressao)
            operador = '+'

            for parte in partes:
                if parte in '+-':
                    operador = parte
                    continue
                if not parte:
                    continue

                if 'd' in parte:
                    if 'k' in parte:
                        dados_part = parte.split('k')
                        qtd, faces = map(int, dados_part[0].split('d'))
                        if 'l' in dados_part[1]:
                            resultados = sorted([random.randint(1, faces) for _ in range(qtd)])
                            selecionados = resultados[:int(dados_part[1].replace('l', ''))]
                            texto = f"{qtd}d{faces} (menor {dados_part[1].replace('l', '')})"
                        else:
                            resultados = sorted([random.randint(1, faces) for _ in range(qtd)])
                            selecionados = resultados[-int(dados_part[1]):]
                            texto = f"{qtd}d{faces} (maior {dados_part[1]})"
                    else:
                        qtd, faces = map(int, parte.split('d'))
                        resultados = [random.randint(1, faces) for _ in range(qtd)]
                        selecionados = resultados
                        texto = f"{qtd}d{faces}"

                    subtotal = sum(selecionados)
                    componentes.append(f"🎯 {texto}\n`{' '.join(map(str, resultados))}` = `{subtotal}`")
                    total += subtotal if operador == '+' else -subtotal
                else:
                    valor = int(parte)
                    sinal = '+' if operador == '+' else '-'
                    componentes.append(f"📝 Modificador\n`{sinal}{valor}`")
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
            await ctx.send(f"❌ Erro: {e}\n💡 Use: `!r 2d20k1+3`")

async def setup(bot):
    await bot.add_cog(Dados(bot))