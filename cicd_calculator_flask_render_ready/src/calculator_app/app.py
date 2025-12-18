import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="templates")

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

ALLOWED_OPS = {"+", "-", "*", "/"}

def parse_number(value: str):
    try:
        return float(value)
    except Exception:
        raise ValueError("INVALID_NUMBER")

@app.post("/calc")
def calc():
    data = request.get_json(silent=True) or {}
    op = data.get("op")
    a = data.get("a")
    b = data.get("b")

    if op not in ALLOWED_OPS:
        return jsonify({"error": "INVALID_OPERATOR"}), 400

    try:
        a = parse_number(str(a))
        b = parse_number(str(b))
    except ValueError:
        return jsonify({"error": "INVALID_NUMBER"}), 400

    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    else:
        if b == 0:
            return jsonify({"error": "DIVIDE_BY_ZERO"}), 400
        result = a / b

    return jsonify({"op": op, "a": a, "b": b, "result": result}), 200

def main():
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    main()
