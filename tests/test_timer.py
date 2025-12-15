import time
from timer_app.app import app

def client():
    return app.test_client()

def reset_timer(c):
    state = c.get("/timer").get_json()["state"]
    if state == "running":
        c.post("/timer/stop")
    c.post("/timer/reset")

def test_initial_state_should_be_stopped():
    c = client()
    reset_timer(c)
    body = c.get("/timer").get_json()
    assert body["state"] == "stopped"
    assert body["elapsed_ms"] == 0
    assert body["laps"] == []

def test_start_and_double_start():
    c = client()
    reset_timer(c)
    assert c.post("/timer/start").status_code == 200
    res = c.post("/timer/start")
    assert res.status_code == 409
    assert res.get_json() == {"error": "ALREADY_RUNNING"}

def test_stop_freezes_time():
    c = client()
    reset_timer(c)
    c.post("/timer/start")
    time.sleep(0.02)
    stop = c.post("/timer/stop").get_json()
    elapsed = stop["elapsed_ms"]
    time.sleep(0.02)
    after = c.get("/timer").get_json()["elapsed_ms"]
    assert after == elapsed
