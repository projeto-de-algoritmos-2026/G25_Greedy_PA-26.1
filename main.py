import sys
import subprocess
from coin_change import CurrencyManager, to_cents, greedy_change, convert_currency, format_money

def fallback_terminal() -> None:
    print("Conversor de moeda com otimizacao de troco (Fallback Terminal)")
    print("--------------------------------------------------------------")
    manager = CurrencyManager()
    
    print("Moedas disponiveis:")
    for currency in manager.list_all():
        print(f"- {currency.code}: {currency.name} (1 {currency.code} = R$ {currency.brl_rate:.4f})")

    try:
        amount = float(input("\nInforme o valor de origem: ").replace(",", "."))
        from_code = input("Moeda de origem (ex: BRL): ").strip().upper()
        to_code = input("Converter para qual moeda? ").strip().upper()
        
        source = manager.get(from_code)
        target = manager.get(to_code)
        
        if not source or not target:
            print("Moeda nao encontrada!")
            return

        converted = convert_currency(amount, source, target)
        converted_cents = to_cents(str(converted))
        change = greedy_change(converted_cents, target.denominations)
        
        print("\nResultado da conversao")
        print(f"Valor original: {source.symbol} {amount:.2f}")
        print(f"Valor convertido: {target.symbol} {converted:.2f}")
        
        print("\nCombinacao gerada pelo algoritmo greedy:")
        for denomination, quantity in change:
            print(f"{quantity} x {format_money(denomination, target)}")

    except ValueError as error:
        print(f"\nErro: {error}")

def main() -> None:
    print("Iniciando a Interface Visual do Conversor de Moedas...")
    print("Se o navegador nao abrir, acesse: http://127.0.0.1:5000")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nServidor encerrado.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--terminal":
        fallback_terminal()
    else:
        main()

