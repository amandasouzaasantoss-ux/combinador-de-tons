"""Combinador de Tons de Pele

Dada uma cor de pele (hex ou RGB), encontra os tons de base mais proximos
de um catalogo, usando o espaco de cor CIELAB e a diferenca de cor
CIEDE2000 (Delta E 2000), padrao usado na industria de cor.

Usa apenas a biblioteca padrao do Python (nenhuma instalacao necessaria).
"""

import argparse
import html
import json
import math
from pathlib import Path

CATALOGO_PADRAO = Path(__file__).with_name("tons.json")


# ---------------------------------------------------------------------------
# 1) Conversao de cores
# ---------------------------------------------------------------------------

def hex_para_rgb(codigo):
    """Converte '#C68642' (ou 'C68642', '#C84') em (198, 134, 66)."""
    c = str(codigo).strip().lstrip("#")
    if len(c) == 3:
        c = "".join(letra * 2 for letra in c)
    if len(c) != 6:
        raise ValueError(f"Codigo de cor invalido: {codigo!r}")
    try:
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"Codigo de cor invalido: {codigo!r}") from None


def rgb_para_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def rgb_para_lab(rgb):
    """Converte sRGB (0-255) para CIELAB (iluminante D65)."""
    def linear(canal):
        c = canal / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(v) for v in rgb)
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b

    def f(t):
        if t > (6 / 29) ** 3:
            return t ** (1 / 3)
        return t / (3 * (6 / 29) ** 2) + 4 / 29

    fx, fy, fz = f(x / 0.95047), f(y / 1.0), f(z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


# ---------------------------------------------------------------------------
# 2) Diferenca de cor (CIEDE2000)
# ---------------------------------------------------------------------------

def delta_e_2000(lab1, lab2):
    """Diferenca perceptual entre duas cores em CIELAB (CIEDE2000)."""
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2

    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    c_medio = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(c_medio ** 7 / (c_medio ** 7 + 25 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if c1p else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if c2p else 0.0

    dl = l2 - l1
    dc = c2p - c1p
    if c1p * c2p == 0:
        dh = 0.0
    else:
        dh = h2p - h1p
        if dh > 180:
            dh -= 360
        elif dh < -180:
            dh += 360
    d_h_grande = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh / 2))

    l_medio = (l1 + l2) / 2
    c_medio_p = (c1p + c2p) / 2
    if c1p * c2p == 0:
        h_medio = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        h_medio = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        h_medio = (h1p + h2p + 360) / 2
    else:
        h_medio = (h1p + h2p - 360) / 2

    t = (1
         - 0.17 * math.cos(math.radians(h_medio - 30))
         + 0.24 * math.cos(math.radians(2 * h_medio))
         + 0.32 * math.cos(math.radians(3 * h_medio + 6))
         - 0.20 * math.cos(math.radians(4 * h_medio - 63)))
    delta_theta = 30 * math.exp(-(((h_medio - 275) / 25) ** 2))
    rc = 2 * math.sqrt(c_medio_p ** 7 / (c_medio_p ** 7 + 25 ** 7))
    sl = 1 + (0.015 * (l_medio - 50) ** 2) / math.sqrt(20 + (l_medio - 50) ** 2)
    sc = 1 + 0.045 * c_medio_p
    sh = 1 + 0.015 * c_medio_p * t
    rt = -math.sin(math.radians(2 * delta_theta)) * rc

    return math.sqrt(
        (dl / sl) ** 2
        + (dc / sc) ** 2
        + (d_h_grande / sh) ** 2
        + rt * (dc / sc) * (d_h_grande / sh)
    )


def descrever_diferenca(delta_e):
    """Traduz o Delta E em uma frase facil de entender."""
    if delta_e < 1:
        return "praticamente identico"
    if delta_e < 2:
        return "diferenca quase imperceptivel"
    if delta_e < 3.5:
        return "diferenca perceptivel so de perto"
    if delta_e < 5:
        return "diferenca visivel"
    return "tom bem diferente"


# ---------------------------------------------------------------------------
# 3) Catalogo e busca
# ---------------------------------------------------------------------------

def carregar_catalogo(caminho=CATALOGO_PADRAO):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)["tons"]


def melhores_tons(rgb, catalogo, quantos=3):
    """Retorna os 'quantos' tons mais proximos, do melhor para o pior."""
    lab_pele = rgb_para_lab(rgb)
    resultados = []
    for tom in catalogo:
        delta_e = delta_e_2000(lab_pele, rgb_para_lab(hex_para_rgb(tom["hex"])))
        resultados.append({**tom, "delta_e": delta_e})
    resultados.sort(key=lambda item: item["delta_e"])
    return resultados[:quantos]


# ---------------------------------------------------------------------------
# 4) Saidas: texto no terminal e relatorio HTML
# ---------------------------------------------------------------------------

def mostrar_no_terminal(rgb, resultados):
    print(f"\nCor informada: {rgb_para_hex(rgb)}")
    print("Tons mais proximos:\n")
    for posicao, tom in enumerate(resultados, start=1):
        print(f"  {posicao}. {tom['codigo']} - {tom['nome']} "
              f"(subtom {tom['subtom']}, {tom['hex']})")
        print(f"     Delta E = {tom['delta_e']:.2f}: "
              f"{descrever_diferenca(tom['delta_e'])}")
    print("\nAviso: ferramenta demonstrativa. Cores de tela variam com a luz "
          "e o aparelho; para escolher uma base de verdade, teste no rosto "
          "com luz natural.")


def gerar_relatorio_html(rgb, resultados, caminho):
    e = html.escape
    cartoes = []
    for posicao, tom in enumerate(resultados, start=1):
        cartoes.append(
            '<div class="cartao">'
            f'<div class="amostra" style="background:{e(tom["hex"])}"></div>'
            f'<h3>{posicao}. {e(tom["codigo"])} &middot; {e(tom["nome"])}</h3>'
            f'<p>Subtom {e(tom["subtom"])} &middot; {e(tom["hex"])}</p>'
            f'<p><strong>Delta E {tom["delta_e"]:.2f}</strong>: '
            f'{e(descrever_diferenca(tom["delta_e"]))}</p></div>'
        )
    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatorio de Tons</title>
<style>
body{{font-family:system-ui,Arial,sans-serif;background:#faf7f5;color:#2b2b2b;max-width:760px;margin:0 auto;padding:24px 16px}}
h1{{color:#7a3b4a}} .topo{{display:flex;gap:16px;align-items:center;margin-bottom:24px}}
.topo .amostra{{width:90px;height:90px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 6px #0003}}
.cartao{{background:#fff;border-radius:14px;padding:16px;margin-bottom:14px;box-shadow:0 1px 4px #0002}}
.cartao .amostra{{height:60px;border-radius:10px;margin-bottom:10px}}
.cartao h3{{margin:0 0 4px}} .cartao p{{margin:2px 0}}
.aviso{{color:#666;font-size:.85rem;margin-top:24px}}
</style></head><body>
<h1>Combinador de Tons de Pele</h1>
<div class="topo"><div class="amostra" style="background:{e(rgb_para_hex(rgb))}"></div>
<div><strong>Cor informada</strong><br>{e(rgb_para_hex(rgb))}</div></div>
{''.join(cartoes)}
<p class="aviso">Ferramenta demonstrativa com catalogo ficticio. Cores de tela variam
com a luz e o aparelho; para escolher uma base de verdade, teste no rosto com luz natural.</p>
</body></html>"""
    Path(caminho).write_text(pagina, encoding="utf-8")


# ---------------------------------------------------------------------------
# 5) Linha de comando
# ---------------------------------------------------------------------------

def main(argumentos=None):
    parser = argparse.ArgumentParser(
        description="Encontra o tom de base mais proximo de uma cor de pele.")
    parser.add_argument("cor", nargs="?",
                        help="cor da pele em hex, por exemplo #C68642")
    parser.add_argument("--quantos", type=int, default=3,
                        help="quantos tons mostrar (padrao: 3)")
    parser.add_argument("--html", metavar="ARQUIVO",
                        help="tambem salva um relatorio visual, ex.: relatorio.html")
    args = parser.parse_args(argumentos)

    codigo = args.cor or input("Digite a cor da pele em hex (ex.: #C68642): ")
    try:
        rgb = hex_para_rgb(codigo)
    except ValueError as erro:
        print(erro)
        return 1

    resultados = melhores_tons(rgb, carregar_catalogo(), args.quantos)
    mostrar_no_terminal(rgb, resultados)
    if args.html:
        gerar_relatorio_html(rgb, resultados, args.html)
        print(f"\nRelatorio salvo em: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
