from coin_change import CURRENCIES, build_change_report, format_money, parse_money


def show_available_currencies() -> None:
    print("Moedas disponiveis:")
    for currency in CURRENCIES.values():
        print(f"- {currency.code}: {currency.name} (1 {currency.code} = R$ {currency.brl_rate:.2f})")


def main() -> None:
    print("Conversor de moeda com otimizacao de troco")
    print("-------------------------------------------")
    show_available_currencies()

    try:
        amount_brl = parse_money(input("\nInforme o valor em reais: R$ "))
        currency_code = input("Converter para qual moeda? ").strip().upper()
        report = build_change_report(amount_brl, currency_code)
    except ValueError as error:
        print(f"\nErro: {error}")
        return

    currency = report["currency"]
    print("\nResultado da conversao")
    print(f"Valor original: R$ {amount_brl:.2f}".replace(".", ","))
    print(f"Valor convertido: {currency.symbol} {report['converted']:.2f}".replace(".", ","))
    print(f"Quantidade minima de cedulas/moedas: {report['total_items']}")

    print("\nCombinacao gerada pelo algoritmo greedy:")
    for denomination, quantity in report["change"]:
        print(f"{quantity} x {format_money(denomination, currency)}")


if __name__ == "__main__":
    main()
