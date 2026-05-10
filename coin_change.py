"""
Módulo de conversão de moedas e algoritmo guloso (Greedy Coin Change).

Contém as classes e funções responsáveis por:
- Representar moedas e suas denominações
- Gerenciar moedas dinamicamente via JSON
- Controlar estoque de cédulas/moedas
- Algoritmo guloso para decomposição em cédulas/moedas
- Conversão entre quaisquer moedas cadastradas
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional



@dataclass
class Currency:
    """Representa uma moeda com código, nome, símbolo, cotação em BRL e denominações."""

    code: str
    name: str
    symbol: str
    brl_rate: float
    denominations: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Currency":
        return cls(**data)


#Default
DEFAULT_CURRENCIES: list[dict] = [
    {
        "code": "BRL",
        "name": "Real brasileiro",
        "symbol": "R$",
        "brl_rate": 1.00,
        "denominations": [20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1],
    },
    {
        "code": "USD",
        "name": "Dólar americano",
        "symbol": "US$",
        "brl_rate": 5.00,
        "denominations": [10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1],
    },
    {
        "code": "EUR",
        "name": "Euro",
        "symbol": "€",
        "brl_rate": 5.50,
        "denominations": [50000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1],
    },
    {
        "code": "GBP",
        "name": "Libra esterlina",
        "symbol": "£",
        "brl_rate": 6.40,
        "denominations": [5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1],
    },
]

#  Gerenciador de moedas
class CurrencyManager:
    """Gerencia moedas cadastradas, carregando e salvando em currencies.json."""

    def __init__(self, filepath: str = "currencies.json"):
        self._filepath = filepath
        self._currencies: dict[str, Currency] = {}
        self.load()

    # --- Persistência ---

    def load(self) -> None:
        """Carrega moedas do JSON. Se o arquivo não existir, cria com padrões."""
        if not os.path.exists(self._filepath):
            self._currencies = {d["code"]: Currency.from_dict(d) for d in DEFAULT_CURRENCIES}
            self.save()
            return
        with open(self._filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._currencies = {item["code"]: Currency.from_dict(item) for item in data}

    def save(self) -> None:
        """Persiste moedas no JSON."""
        data = [c.to_dict() for c in self._currencies.values()]
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # CRUDzão

    def list_all(self) -> list[Currency]:
        return list(self._currencies.values())

    def get(self, code: str) -> Optional[Currency]:
        return self._currencies.get(code.upper())

    def add_currency(self, code: str, name: str, symbol: str, brl_rate: float, denominations: list[int]) -> Currency:
        code = code.upper().strip()
        if code in self._currencies:
            raise ValueError(f"Moeda '{code}' já existe.")
        if brl_rate <= 0:
            raise ValueError("A cotação deve ser maior que zero.")
        if not denominations:
            raise ValueError("Informe ao menos uma denominação.")

        currency = Currency(
            code=code,
            name=name.strip(),
            symbol=symbol.strip(),
            brl_rate=brl_rate,
            denominations=sorted(denominations, reverse=True),
        )
        self._currencies[code] = currency
        self.save()
        return currency

    def update_rate(self, code: str, new_rate: float) -> Currency:
        code = code.upper()
        if code not in self._currencies:
            raise ValueError(f"Moeda '{code}' não encontrada.")
        if new_rate <= 0:
            raise ValueError("A cotação deve ser maior que zero.")
        self._currencies[code].brl_rate = new_rate
        self.save()
        return self._currencies[code]

    def remove_currency(self, code: str) -> None:
        code = code.upper()
        if code == "BRL":
            raise ValueError("Não é possível remover o Real (BRL).")
        if code not in self._currencies:
            raise ValueError(f"Moeda '{code}' não encontrada.")
        del self._currencies[code]
        self.save()




#Estoque das cédulas
class StockManager:
    """Gerencia estoque de cédulas/moedas, persistindo em stock.json."""

    def __init__(self, filepath: str = "stock.json"):
        self._filepath = filepath
        self._stock: dict[str, dict[str, int]] = {}
        self.load()

    # persistência

    def load(self) -> None:
        if not os.path.exists(self._filepath):
            self._stock = {}
            self.save()
            return
        with open(self._filepath, "r", encoding="utf-8") as f:
            self._stock = json.load(f)

    def save(self) -> None:
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._stock, f, ensure_ascii=False, indent=2)

    #operações

    def get_stock(self, currency_code: str) -> dict[str, int]:
        """Retorna estoque da moeda. Chaves são denominações (str), valores são quantidades."""
        return dict(self._stock.get(currency_code.upper(), {}))

    def set_stock(self, currency_code: str, stock_data: dict[str, int]) -> None:
        """Define estoque completo para uma moeda."""
        code = currency_code.upper()
        self._stock[code] = {str(k): int(v) for k, v in stock_data.items()}
        self.save()

    def set_denomination_qty(self, currency_code: str, denomination: int, quantity: int) -> None:
        """Define quantidade de uma denominação específica."""
        code = currency_code.upper()
        if code not in self._stock:
            self._stock[code] = {}
        self._stock[code][str(denomination)] = max(0, quantity)
        self.save()

    def deduct(self, currency_code: str, change_list: list[tuple[int, int]]) -> None:
        """Deduz do estoque as quantidades usadas na conversão."""
        code = currency_code.upper()
        stock = self._stock.get(code, {})
        for denomination, qty in change_list:
            key = str(denomination)
            current = stock.get(key, 0)
            stock[key] = max(0, current - qty)
        self._stock[code] = stock
        self.save()

    def has_sufficient(self, currency_code: str, change_list: list[tuple[int, int]]) -> bool:
        """Verifica se o estoque é suficiente para a lista de troco."""
        stock = self._stock.get(currency_code.upper(), {})
        for denomination, qty in change_list:
            available = stock.get(str(denomination), 0)
            if available < qty:
                return False
        return True



def to_cents(value: float) -> int:
    """Converte valor numérico para centavos inteiros."""
    return int(round(float(value) * 100))


def from_cents(cents: int) -> float:
    """Converte centavos inteiros para float."""
    return round(cents / 100.0, 2)


def convert_currency(amount: float, source: Currency, target: Currency) -> float:
    """Converte um valor de qualquer moeda para qualquer outra, via BRL como intermediário."""
    amount_brl = amount * source.brl_rate
    converted = amount_brl / target.brl_rate
    return round(converted, 2)


def format_money(cents: int, currency: Currency) -> str:
    """Formata centavos como string monetária."""
    amount = float(from_cents(cents))
    return f"{currency.symbol} {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


#  algoritmo da moeda

def greedy_change(amount_cents: int, denominations: list[int]) -> list[tuple[int, int]]:
    """
    Algoritmo guloso clássico: decompõe um valor em centavos na menor
    quantidade possível de cédulas/moedas, sempre pegando a maior
    denominação possível primeiro.
    """
    if amount_cents < 0:
        raise ValueError("O valor em centavos não pode ser negativo.")

    remaining = amount_cents
    change: list[tuple[int, int]] = []

    for denomination in sorted(denominations, reverse=True):
        quantity = remaining // denomination
        if quantity:
            change.append((denomination, quantity))
            remaining %= denomination

    if remaining != 0:
        raise ValueError("Não foi possível representar o valor com as denominações informadas.")

    return change


def greedy_change_with_stock(
    amount_cents: int,
    denominations: list[int],
    stock: dict[str, int],
) -> list[tuple[int, int]]:
    """
    Algoritmo guloso limitado pelo estoque disponível.
    Só usa a quantidade de cédulas/moedas que realmente existem.
    """
    if amount_cents < 0:
        raise ValueError("O valor em centavos não pode ser negativo.")

    remaining = amount_cents
    change: list[tuple[int, int]] = []

    for denomination in sorted(denominations, reverse=True):
        available = stock.get(str(denomination), 0)
        if available <= 0:
            continue
        max_needed = remaining // denomination
        quantity = min(max_needed, available)
        if quantity:
            change.append((denomination, quantity))
            remaining -= denomination * quantity

    if remaining != 0:
        raise ValueError(
            "Estoque insuficiente! Não foi possível completar o valor "
            "com as cédulas/moedas disponíveis."
        )

    return change
