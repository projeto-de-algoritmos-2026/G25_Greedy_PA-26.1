from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


@dataclass(frozen=True)
class Currency:
    code: str
    name: str
    symbol: str
    brl_rate: Decimal
    denominations: tuple[int, ...]


CURRENCIES: dict[str, Currency] = {
    "BRL": Currency(
        code="BRL",
        name="Real brasileiro",
        symbol="R$",
        brl_rate=Decimal("1.00"),
        denominations=(20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1),
    ),
    "USD": Currency(
        code="USD",
        name="Dolar americano",
        symbol="US$",
        brl_rate=Decimal("5.00"),
        denominations=(10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1),
    ),
    "EUR": Currency(
        code="EUR",
        name="Euro",
        symbol="€",
        brl_rate=Decimal("5.50"),
        denominations=(50000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1),
    ),
    "GBP": Currency(
        code="GBP",
        name="Libra esterlina",
        symbol="£",
        brl_rate=Decimal("6.40"),
        denominations=(5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1),
    ),
}


def parse_money(value: str) -> Decimal:
    normalized = value.strip().replace(" ", "")
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    try:
        amount = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError("Valor monetario invalido.") from exc

    if amount <= 0:
        raise ValueError("O valor precisa ser maior que zero.")

    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def to_cents(value: Decimal) -> int:
    return int((value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def from_cents(cents: int) -> Decimal:
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def convert_from_brl(amount_brl: Decimal, target: Currency) -> Decimal:
    converted = amount_brl / target.brl_rate
    return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def greedy_change(amount_cents: int, denominations: tuple[int, ...]) -> list[tuple[int, int]]:
    if amount_cents < 0:
        raise ValueError("O valor em centavos nao pode ser negativo.")

    remaining = amount_cents
    change: list[tuple[int, int]] = []

    for denomination in sorted(denominations, reverse=True):
        quantity = remaining // denomination
        if quantity:
            change.append((denomination, quantity))
            remaining %= denomination

    if remaining != 0:
        raise ValueError("Nao foi possivel representar o valor com as denominacoes informadas.")

    return change


def format_money(cents: int, currency: Currency) -> str:
    amount = from_cents(cents)
    return f"{currency.symbol} {amount:.2f}".replace(".", ",")


def build_change_report(amount_brl: Decimal, currency_code: str) -> dict[str, object]:
    code = currency_code.upper()
    if code not in CURRENCIES:
        available = ", ".join(CURRENCIES)
        raise ValueError(f"Moeda indisponivel. Opcoes: {available}.")

    currency = CURRENCIES[code]
    converted = convert_from_brl(amount_brl, currency)
    converted_cents = to_cents(converted)
    change = greedy_change(converted_cents, currency.denominations)

    return {
        "currency": currency,
        "converted": converted,
        "converted_cents": converted_cents,
        "change": change,
        "total_items": sum(quantity for _, quantity in change),
    }
