from calculator_app.app import app

def test_health_should_return_ok():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}

def test_index_should_load():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"CI/CD Calculator" in res.data
