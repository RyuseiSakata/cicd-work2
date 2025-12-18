import time
import os
from flask import Flask, jsonify, render_template
import subprocess

try:
    from timer_app.lap import register_lap_routes
    from timer_app.world_clock import register_clock_routes
except ModuleNotFoundError:
    from lap import register_lap_routes
    from world_clock import register_clock_routes


def get_git_commit():
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


app = Flask(__name__, template_folder="templates")


def deploy_metadata():
    return {
        "commit": get_git_commit(),
    }


# =========================
# 内部状態（シンプル実装）
# =========================
# TODO 1: タイマーの状態を管理する変数を定義してください
# ヒント: state は "stopped" または "running"（初期値: "stopped"）
# ヒント: start_time は time.monotonic() の値（初期値: None）
# ヒント: elapsed_ms は累積経過時間（初期値: 0）
# ヒント: laps はラップ記録のリスト（初期値: []）

state = ____
start_time = ____
elapsed_ms = ____
laps = ____


def get_state():
    return state


def get_laps():
    return laps


# =========================
# 補助関数
# =========================
def current_elapsed_ms():
    """現在の経過時間（ms）を返す"""
    global elapsed_ms, start_time, state
    
    # TODO 2: タイマーが実行中の場合の経過時間を計算してください
    # ヒント: 累積時間 + (現在時刻 - 開始時刻) × 1000
    if state == ____ and start_time is not None:
        return elapsed_ms + int((time.monotonic() - ____) * ____)
    
    return elapsed_ms


# =========================
# 画面（タイマーアプリ）
# =========================
@app.get("/")
def index():
    meta = deploy_metadata()
    return render_template(
        "index.html",
        commit=meta["commit"],
    )


# =========================
# API
# =========================
@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/timer")
def get_timer():
    return (
        jsonify({"state": state, "elapsed_ms": current_elapsed_ms(), "laps": laps}),
        200,
    )


@app.post("/timer/start")
def start_timer():
    global state, start_time
    
    # TODO 3: 既に実行中の場合はエラーを返し、そうでなければタイマーを開始してください
    # ヒント: state が "running" の場合、HTTPステータス 409 で "ALREADY_RUNNING" を返す
    # ヒント: state を "running" に、start_time を time.monotonic() に設定
    
    if state == ____:
        return jsonify({"error": ____}), ____

    state = ____
    start_time = ____
    
    return jsonify({"state": state, "elapsed_ms": 0}), 200


@app.post("/timer/stop")
def stop_timer():
    global state, elapsed_ms, start_time
    
    # TODO 4: 既に停止中の場合はエラーを返し、そうでなければタイマーを停止してください
    # ヒント: state が "stopped" の場合、HTTPステータス 409 で "ALREADY_STOPPED" を返す
    # 重要: elapsed_ms を先に更新してから state を変更すること
    
    if state == ____:
        return jsonify({"error": ____}), ____

    elapsed_ms = ____
    start_time = ____
    state = ____

    return jsonify({"state": state, "elapsed_ms": elapsed_ms}), 200


# =========================
# ラップ機能（完成版を提供）
# =========================
register_lap_routes(
    app=app,
    current_elapsed_ms=current_elapsed_ms,
    get_state=get_state,
    get_laps=get_laps,
)


@app.post("/timer/reset")
def reset_timer():
    global state, start_time, elapsed_ms, laps
    if state == "running":
        return jsonify({"error": "CANNOT_RESET_WHILE_RUNNING"}), 409

    state = "stopped"
    start_time = None
    elapsed_ms = 0
    laps = []

    return jsonify({"state": state, "elapsed_ms": 0, "laps": []}), 200


# =========================
# Clock API（穴埋め版を使用）
# =========================
register_clock_routes(app=app)


# =========================
# ローカル実行用
# =========================
def main():
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
