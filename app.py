"""
Servidor Flask para o Conversor de Moedas com Algoritmo Guloso.

Fornece uma API REST JSON e serve a interface visual HTML.
"""

import webbrowser
import threading

from flask import Flask, render_template, request, jsonify

from coin_change import (
    CurrencyManager,
    StockManager,
    convert_currency,
    to_cents,
    greedy_change,
    greedy_change_with_stock,
    format_money,
    from_cents,
)

app = Flask(__name__)

# Instâncias globais dos gerenciadores
currency_manager = CurrencyManager()
stock_manager = StockManager()




@app.route("/")
def index():
    """Serve a interface visual."""
    return render_template("index.html")



@app.route("/api/currencies", methods=["GET"])
def api_list_currencies():
    """Lista todas as moedas cadastradas."""
    currencies = currency_manager.list_all()
    return jsonify([c.to_dict() for c in currencies])


@app.route("/api/currencies", methods=["POST"])
def api_add_currency():
    """Adiciona uma nova moeda."""
    data = request.get_json()
    try:
        code = data.get("code", "")
        name = data.get("name", "")
        symbol = data.get("symbol", "")
        brl_rate = float(data.get("brl_rate", 0))
        denominations = [int(d) for d in data.get("denominations", [])]

        currency = currency_manager.add_currency(code, name, symbol, brl_rate, denominations)
        return jsonify({"success": True, "currency": currency.to_dict()}), 201
    except (ValueError, TypeError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/currencies/<code>/rate", methods=["PUT"])
def api_update_rate(code):
    """Atualiza a cotação de uma moeda."""
    data = request.get_json()
    try:
        new_rate = float(data.get("brl_rate", 0))
        currency = currency_manager.update_rate(code, new_rate)
        return jsonify({"success": True, "currency": currency.to_dict()})
    except (ValueError, TypeError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/currencies/<code>", methods=["DELETE"])
def api_delete_currency(code):
    """Remove uma moeda."""
    try:
        currency_manager.remove_currency(code)
        return jsonify({"success": True})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400



@app.route("/api/convert", methods=["POST"])
def api_convert():
    """
    Realiza conversão entre duas moedas com decomposição gulosa.

    Body JSON esperado:
    {
        "amount": 100.00,
        "from": "BRL",
        "to": "USD",
        "use_stock": false
    }
    """
    data = request.get_json()
    try:
        amount = float(data.get("amount", 0))
        from_code = data.get("from", "").upper()
        to_code = data.get("to", "").upper()
        use_stock = data.get("use_stock", False)

        if amount <= 0:
            raise ValueError("O valor precisa ser maior que zero.")

        source = currency_manager.get(from_code)
        target = currency_manager.get(to_code)

        if not source:
            raise ValueError(f"Moeda de origem '{from_code}' não encontrada.")
        if not target:
            raise ValueError(f"Moeda de destino '{to_code}' não encontrada.")
        if from_code == to_code:
            raise ValueError("As moedas de origem e destino devem ser diferentes.")

        # Conversão
        converted = convert_currency(amount, source, target)
        converted_cents = to_cents(converted)

        # Algoritmo guloso
        if use_stock:
            stock = stock_manager.get_stock(to_code)
            change = greedy_change_with_stock(converted_cents, target.denominations, stock)
        else:
            change = greedy_change(converted_cents, target.denominations)

        # Formatar resultado
        total_items = sum(qty for _, qty in change)
        change_formatted = []
        for denomination, qty in change:
            change_formatted.append({
                "denomination": denomination,
                "denomination_formatted": format_money(denomination, target),
                "quantity": qty,
            })

        result = {
            "success": True,
            "from_code": from_code,
            "from_symbol": source.symbol,
            "to_code": to_code,
            "to_symbol": target.symbol,
            "original_amount": amount,
            "converted_amount": converted,
            "total_items": total_items,
            "change": change_formatted,
            "used_stock": use_stock,
        }
        return jsonify(result)

    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/convert/confirm", methods=["POST"])
def api_confirm_conversion():
    """Confirma a conversão e deduz do estoque."""
    data = request.get_json()
    try:
        to_code = data.get("to", "").upper()
        change = [(item["denomination"], item["quantity"]) for item in data.get("change", [])]

        if not stock_manager.has_sufficient(to_code, change):
            return jsonify({"success": False, "error": "Estoque insuficiente para confirmar."}), 400

        stock_manager.deduct(to_code, change)
        return jsonify({"success": True, "message": "Estoque atualizado com sucesso!"})
    except (ValueError, KeyError, TypeError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/stock/<code>", methods=["GET"])
def api_get_stock(code):
    """Retorna o estoque de uma moeda."""
    code = code.upper()
    currency = currency_manager.get(code)
    if not currency:
        return jsonify({"success": False, "error": f"Moeda '{code}' não encontrada."}), 404

    stock = stock_manager.get_stock(code)
    # Garante que todas as denominações apareçam
    stock_list = []
    for denom in currency.denominations:
        stock_list.append({
            "denomination": denom,
            "denomination_formatted": format_money(denom, currency),
            "quantity": stock.get(str(denom), 0),
        })

    return jsonify({
        "success": True,
        "code": code,
        "symbol": currency.symbol,
        "stock": stock_list,
    })


@app.route("/api/stock/<code>", methods=["PUT"])
def api_update_stock(code):
    """Atualiza o estoque de uma moeda."""
    code = code.upper()
    currency = currency_manager.get(code)
    if not currency:
        return jsonify({"success": False, "error": f"Moeda '{code}' não encontrada."}), 404

    data = request.get_json()
    stock_data = data.get("stock", {})
    stock_manager.set_stock(code, stock_data)
    return jsonify({"success": True, "message": "Estoque atualizado!"})


def open_browser():
    """Abre o navegador automaticamente após o servidor iniciar."""
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    timer = threading.Timer(1.5, open_browser)
    timer.daemon = True
    timer.start()
    print("=" * 50)
    print("  Conversor de Moedas - Algoritmo Guloso")
    print("  Acesse: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=False, port=5000)
