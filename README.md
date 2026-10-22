# Combinador de Tons de Pele

Programa em Python que recebe a cor da pele (código hex) e encontra os tons de base mais próximos de um catálogo, usando ciência de cor: espaço **CIELAB** e diferença de cor **CIEDE2000 (Delta E 2000)**, padrão usado na indústria para medir quão diferentes duas cores parecem aos olhos humanos.

> **Aviso:** projeto de portfólio e demonstrativo. O catálogo (`tons.json`) é **fictício** e não representa nenhuma marca. Cores de tela variam com a luz e o aparelho, então não substitui testar a base no rosto.

## Como funciona

1. A cor informada (RGB) é convertida para CIELAB, um espaço de cor em que a distância numérica se aproxima da percepção visual.
2. A diferença entre a cor da pele e cada tom do catálogo é calculada com a fórmula CIEDE2000.
3. Os tons são ordenados do mais próximo ao mais distante, com uma explicação em linguagem simples:

| Delta E | Significado |
|---|---|
| menor que 1 | praticamente idêntico |
| 1 a 2 | diferença quase imperceptível |
| 2 a 3,5 | perceptível só de perto |
| 3,5 a 5 | diferença visível |
| 5 ou mais | tom bem diferente |

## Como usar

Requer apenas Python 3.8 ou mais novo. Não precisa instalar nada.

```
python combinador_tons.py "#D8AA85"
```

Exemplo de resultado:

```
Cor informada: #D8AA85
Tons mais proximos:

  1. N40 - Bege Medio (subtom neutro, #D2A582)
     Delta E = 1.53: diferenca quase imperceptivel
  2. W35 - Bege Dourado (subtom quente, #DBB088)
     Delta E = 2.11: diferenca perceptivel so de perto
  3. W45 - Mel (subtom quente, #C99A6B)
     Delta E = 5.49: tom bem diferente
```

Opções:

- `--quantos 5`: mostra 5 tons em vez de 3
- `--html relatorio.html`: salva um relatório visual com as amostras de cor
- sem nenhuma cor: o programa pergunta no terminal

## Testes

```
python -m unittest -v
```

Os testes incluem pares de referência publicados na literatura (Sharma, Wu e Dalal, 2005) para validar a implementação do Delta E 2000.

## Estrutura

- `combinador_tons.py`: conversão de cores, cálculo do Delta E, busca e relatório
- `tons.json`: catálogo fictício de 16 tons com subtom frio, neutro ou quente
- `test_combinador.py`: testes automáticos

## Limitações

- Catálogo pequeno e fictício
- A cor informada vem de uma tela, sem calibração nem controle de iluminação
- Não identifica o subtom da pele; usa apenas a cor

## Próximos passos (ideias)

- Ler a cor da pele a partir de uma foto, com correção de iluminação
- Recomendar o subtom (frio, neutro ou quente) com base na cor
- Carregar catálogos reais a partir de arquivo CSV
- Interface web
