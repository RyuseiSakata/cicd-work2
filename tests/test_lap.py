import time
from timer_app.app import app

def client():
    return app.test_client()

def reset_timer(c):
    state = c.get("/timer").get_json()["state"]
    if state == "running":
        c.post("/timer/stop")
    c.post("/timer/reset")

def test_lap_requires_running():
    c = client()
    reset_timer(c)
    res = c.post("/timer/lap")
    assert res.status_code == 409
    assert res.get_json() == {"error": "NOT_RUNNING"}

def test_lap_incremental():
    c = client()
    reset_timer(c)
    c.post("/timer/start")
    time.sleep(0.02)
    l1 = c.post("/timer/lap").get_json()
    time.sleep(0.02)
    l2 = c.post("/timer/lap").get_json()
    assert l2["lap_index"] == 2
    assert l2["lap_elapsed_ms"] == l2["total_elapsed_ms"] - l1["total_elapsed_ms"]
