# G25_Greedy_PA-26.1

**Número do trabalho:** 2 <br>
**Conteúdo do Módulo: Algoritmos Ambiciosos (Coin Change)**

## Alunos

| Matrícula |          Nome Completo           |
| :-------: | :------------------------------: |
| 211062929 | Davi dos Santos Brito Nobre      |
| 221008202 | José Eduardo Vieira do Prado     |

## Sobre o trabalho

Este projeto implementa um **Conversor de Moedas Dinâmico** com cálculo de troco/decomposição usando o **Algoritmo Guloso (Greedy Coin Change)**.

A aplicação evoluiu de um script de terminal para um sistema completo com:
- **Interface Visual Moderna:** Servidor Flask com página HTML e design "Glassmorphism".
- **Gerenciamento Dinâmico:** Cotações atualizáveis através de uma API gratuita externa (Frankfurter) e dados persistidos em `currencies.json`.
- **Controle de Estoque Físico:** Opção de limitar a quantidade de moedas entregues na conversão de acordo com as notas armazenadas fisicamente no "cofre" (persistido em `stock.json`).

## Pré-requisitos

- Python 3.10+
- (Recomendado) Ambiente virtual ativo

## Como Executar

1. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

2. Inicie a aplicação (iniciará o servidor web e abrirá o navegador automaticamente):
   ```bash
   python main.py
   ```

*(Modo Fallback em Terminal)*
Caso não queira ou consiga acessar o navegador, a versão em terminal continua disponível:
```bash
python main.py --terminal
```

## Como o Algoritmo Guloso Funciona?

O algoritmo sempre tenta pegar a **maior nota possível primeiro**.
Exemplo: R$ 85 em notas de [50, 20, 10, 5, 2, 1]
1. Uma nota de 50 (sobram 35)
2. Uma nota de 20 (sobram 15)
3. Uma nota de 10 (sobram 5)
4. Uma nota de 5 (sobram 0)

Com a funcionalidade "Limitar pelo Estoque" ativada, ele verifica o cofre (em `stock.json`) e se não houverem notas de 50, ele é forçado a usar notas menores de forma otimizada, desde que disponíveis.