from datetime import datetime
from zoneinfo import ZoneInfo
from flask import jsonify, request


# =========================
# Clock（世界時計）設定
# =========================
# TODO 1: サポートするタイムゾーンを定義してください
# ヒント: 辞書形式で、キーと値は同じタイムゾーン名
# ヒント: UTC, Asia/Tokyo, America/New_York, Europe/London をサポート

ALLOWED_TZ = {
    ____: "UTC",
    ____: "Asia/Tokyo",
    "America/New_York": ____,
    "Europe/London": ____,
}


# =========================
# Clock API（世界時計）
# =========================
def register_clock_routes(app):
    @app.get("/clock")
    def get_clock():
        # TODO 2: クエリパラメータからタイムゾーンを取得してください
        # ヒント: request.args.get() を使用、デフォルトは "UTC"
        tz = request.args.get(____, ____)
        
        # TODO 3: タイムゾーンが不正な場合はエラーを返してください
        # ヒント: HTTPステータス 400、エラーメッセージは "INVALID_TIMEZONE"
        if tz not in ____:
            return jsonify({"error": ____}), ____

        # TODO 4: 指定されたタイムゾーンで現在時刻を取得してください
        # ヒント: datetime.now() に ZoneInfo() を渡す
        # ヒント: ALLOWED_TZ[tz] でタイムゾーン名を取得
        now = datetime.now(____(____[____]))
        
        # TODO 5: レスポンスを作成してください
        # ヒント: tz, iso（ISOフォーマット）, epoch_ms（ミリ秒単位のエポック時刻）
        # ヒント: now.isoformat() でISO形式の文字列を取得
        # ヒント: now.timestamp() * 1000 でミリ秒単位のエポック時刻
        return (
            jsonify(
                {
                    "tz": ____,
                    "iso": now.____(),
                    "epoch_ms": int(now.____() * ____),
                }
            ),
            200,
        )

    return get_clock
