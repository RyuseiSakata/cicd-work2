import math
from calculator_app.app import app

def post(client, payload):
    return client.post("/calc", json=payload)

# ----------------------------
# 仕様書 3. 計算仕様 S-1（加算）を検証するテスト
# ----------------------------
def test_add():
    # Flaskのテストクライアントを生成する。
    # 実際にサーバを起動せず、APIを疑似的に呼び出すための仕組み。
    client = app.test_client()
    # 仕様書「5. API仕様」に従い、POST /calc に JSON を送信する。
    # a=2, op="+", b=3 は仕様書の例そのもの。
    res = client.post("/calc", json={"a": 2, "op": "+", "b": 3})
    # HTTPステータスコードが200であることを確認。
    # これは「正常に計算が成功した」ことを意味する。
    assert res.status_code == 200
    # レスポンスに含まれる result が 5.0 であることを確認。
    # 仕様書「3. 計算仕様 S-1: 加算」が正しく実装されているかを検証している。
    assert res.get_json()["result"] == 5.0


#引き算を検証するテスト
def test_subtract():
    client = app.test_client()
    res = post(client, {"a": 10, "op": "-", "b": 4})
    assert res.status_code == 200
    assert res.get_json()["result"] == 6.0













    

def test_multiply():
    client = app.test_client()
    res = post(client, {"a": 2, "op": "*", "b": 3})
    assert res.status_code == 200
    assert res.get_json()["result"] == 6.0

def test_divide():
    client = app.test_client()
    res = post(client, {"a": 7, "op": "/", "b": 2})
    assert res.status_code == 200
    assert math.isclose(res.get_json()["result"], 3.5)

def test_divide_by_zero_should_be_400():
    client = app.test_client()
    res = post(client, {"a": 7, "op": "/", "b": 0})
    assert res.status_code == 400
    assert res.get_json() == {"error": "DIVIDE_BY_ZERO"}

def test_invalid_operator_should_be_400():
    client = app.test_client()
    res = post(client, {"a": 1, "op": "%", "b": 2})
    assert res.status_code == 400
    assert res.get_json() == {"error": "INVALID_OPERATOR"}

def test_invalid_number_should_be_400():
    client = app.test_client()
    res = post(client, {"a": "x", "op": "+", "b": 2})
    assert res.status_code == 400
    assert res.get_json() == {"error": "INVALID_NUMBER"}
