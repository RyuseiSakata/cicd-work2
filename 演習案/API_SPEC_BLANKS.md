# Timer App API 仕様書（穴埋め実装用）

## 概要

この仕様書は、穴埋め実装に必要な機能の詳細を記載しています。
- **Part 1**: タイマー機能（timer_blanks.py の TODO 1-4）
- **Part 2**: 世界時計機能（world_clock_blanks.py の TODO 1-5）

---

# Part 1: タイマー機能

## 1. 概要

ストップウォッチ機能を提供します。開始・停止・再開が可能で、経過時間をミリ秒単位で管理します。

## 2. データ構造（TODO 1 に対応）

### 内部状態

アプリケーションは以下の4つのグローバル変数で状態を管理します：

| 変数名 | 型 | 初期値 | 説明 |
|--------|-----|--------|------|
| `state` | str | `"stopped"` | タイマーの状態。`"stopped"` または `"running"` |
| `start_time` | float \| None | `None` | タイマー開始時の `time.monotonic()` の値 |
| `elapsed_ms` | int | `0` | 累積経過時間（ミリ秒）。停止時に保存される |
| `laps` | list | `[]` | ラップ記録のリスト。各要素は辞書形式 |

### 状態遷移

```
[stopped] --start--> [running] --stop--> [stopped]
    ↑                                        |
    +----------------------------------------+
                    再開（累積）
```

## 3. 時間計測の仕様（TODO 2 に対応）

### 経過時間の計算式

#### 実行中（`state == "running"`）の場合

```
現在の経過時間 = elapsed_ms + (現在時刻 - start_time) × 1000
```

- **elapsed_ms**: 前回までの累積時間（ミリ秒）
- **time.monotonic()**: 現在時刻（秒単位）
- **start_time**: 開始時の `time.monotonic()` の値（秒単位）
- **× 1000**: 秒をミリ秒に変換

#### 停止中（`state == "stopped"`）の場合

```
現在の経過時間 = elapsed_ms
```

累積時間は固定され、増加しません。

### time.monotonic() について

- **特徴**: 単調増加する時間（システムクロックの変更に影響されない）
- **単位**: 秒（小数点以下も含む）
- **用途**: 経過時間の計測に最適

**例**:
```python
start = time.monotonic()  # 例: 12345.678
# 3秒待つ...
now = time.monotonic()    # 例: 12348.679
elapsed = now - start     # 3.001秒

elapsed_ms = int(elapsed * 1000)  # 3001ミリ秒
```

## 4. API仕様

### 4.1 GET /timer

タイマーの現在状態を取得します。

**リクエスト**
```http
GET /timer HTTP/1.1
```

**レスポンス (200 OK)**
```json
{
  "state": "stopped",
  "elapsed_ms": 0,
  "laps": []
}
```

### 4.2 POST /timer/start（TODO 3 に対応）

タイマーを開始します。

**リクエスト**
```http
POST /timer/start HTTP/1.1
```

**成功レスポンス (200 OK)**
```json
{
  "state": "running",
  "elapsed_ms": 0
}
```

**エラーレスポンス (409 Conflict)** - 既に実行中の場合
```json
{
  "error": "ALREADY_RUNNING"
}
```

**実装要件**:
1. 現在の `state` が `"running"` の場合、409エラーを返す
2. `state` を `"running"` に変更
3. `start_time` に `time.monotonic()` を設定
4. 200ステータスで成功を返す

### 4.3 POST /timer/stop（TODO 4 に対応）

タイマーを停止します。

**リクエスト**
```http
POST /timer/stop HTTP/1.1
```

**成功レスポンス (200 OK)**
```json
{
  "state": "stopped",
  "elapsed_ms": 5234
}
```

**エラーレスポンス (409 Conflict)** - 既に停止中の場合
```json
{
  "error": "ALREADY_STOPPED"
}
```

**実装要件**:
1. 現在の `state` が `"stopped"` の場合、409エラーを返す
2. **重要**: `elapsed_ms` を `current_elapsed_ms()` で更新（先に実行）
3. `start_time` を `None` にリセット
4. `state` を `"stopped"` に変更
5. 200ステータスで累積時間を返す

**注意**: `elapsed_ms` の更新は、`state` を変更する**前**に行う必要があります。
これは、`current_elapsed_ms()` が `state == "running"` の状態で正しく計算されるためです。

## 5. HTTPステータスコード

| コード | 意味 | 使用場面 |
|-------|------|---------|
| 200 | OK | 正常に処理された |
| 409 | Conflict | 状態が矛盾している（二重開始、二重停止） |

### 409 Conflict の使い方

**409 Conflict** は、リクエストが現在のリソースの状態と矛盾している場合に使用します。

**例**:
- タイマーが実行中なのに、再度 `/timer/start` を呼び出した
- タイマーが停止中なのに、再度 `/timer/stop` を呼び出した

## 6. 使用例

### シナリオ1: 基本的な使い方

```bash
# 1. 初期状態を確認
curl http://localhost:5050/timer
# → {"state":"stopped","elapsed_ms":0,"laps":[]}

# 2. タイマーを開始
curl -X POST http://localhost:5050/timer/start
# → {"state":"running","elapsed_ms":0}

# 3. 3秒待つ
sleep 3

# 4. 経過時間を確認
curl http://localhost:5050/timer
# → {"state":"running","elapsed_ms":3042,"laps":[]}

# 5. タイマーを停止
curl -X POST http://localhost:5050/timer/stop
# → {"state":"stopped","elapsed_ms":3042}
```

### シナリオ2: 再開機能

```bash
# 1. 2秒計測して停止
curl -X POST http://localhost:5050/timer/start
sleep 2
curl -X POST http://localhost:5050/timer/stop
# → {"state":"stopped","elapsed_ms":2015}

# 2. 再度開始して1秒計測
curl -X POST http://localhost:5050/timer/start
sleep 1
curl -X POST http://localhost:5050/timer/stop
# → {"state":"stopped","elapsed_ms":3021}
# 累積時間は 2015 + 1006 = 3021ms
```

### シナリオ3: エラーケース

```bash
# 1. タイマーを開始
curl -X POST http://localhost:5050/timer/start
# → {"state":"running","elapsed_ms":0}

# 2. 再度開始を試みる（エラー）
curl -X POST http://localhost:5050/timer/start
# → {"error":"ALREADY_RUNNING"}
# HTTPステータス: 409 Conflict
```

---

# Part 2: 世界時計機能

## 1. 概要

指定されたタイムゾーンの現在時刻を取得する機能です。
4つのタイムゾーン（UTC, Tokyo, New York, London）をサポートします。

## 2. データ構造（TODO 1 に対応）

### サポートするタイムゾーン

以下の4つのタイムゾーンをサポートします：

| タイムゾーン名 | IANA識別子 | 説明 |
|--------------|-----------|------|
| UTC | UTC | 協定世界時 |
| Asia/Tokyo | Asia/Tokyo | 日本標準時（JST） |
| America/New_York | America/New_York | 米国東部時間（EST/EDT） |
| Europe/London | Europe/London | 英国時間（GMT/BST） |

### タイムゾーン辞書の定義

```python
ALLOWED_TZ = {
    "UTC": "UTC",
    "Asia/Tokyo": "Asia/Tokyo",
    "America/New_York": "America/New_York",
    "Europe/London": "Europe/London",
}
```

**形式**: `{キー: 値}` の辞書形式で、キーと値は同じ文字列

## 3. API仕様

### 3.1 GET /clock（TODO 2-5 に対応）

指定されたタイムゾーンの現在時刻を取得します。

**リクエスト**
```http
GET /clock?tz=Asia/Tokyo HTTP/1.1
```

**クエリパラメータ**:

| パラメータ名 | 型 | 必須 | デフォルト | 説明 |
|------------|-----|------|----------|------|
| `tz` | string | No | `"UTC"` | タイムゾーン名 |

**成功レスポンス (200 OK)**
```json
{
  "tz": "Asia/Tokyo",
  "iso": "2024-12-18T15:30:45.123456+09:00",
  "epoch_ms": 1702879845123
}
```

**レスポンスフィールド**:

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| `tz` | string | リクエストされたタイムゾーン名 |
| `iso` | string | ISO 8601形式の時刻文字列 |
| `epoch_ms` | integer | Unixエポックからのミリ秒数 |

**エラーレスポンス (400 Bad Request)** - 不正なタイムゾーンの場合
```json
{
  "error": "INVALID_TIMEZONE"
}
```

## 4. 実装要件（TODO 2-5 の詳細）

### TODO 2: クエリパラメータの取得

**要件**:
- `request.args.get()` を使用してクエリパラメータ `"tz"` を取得
- パラメータが指定されていない場合は、デフォルト値 `"UTC"` を使用

**実装例の考え方**:
```python
# request.args.get(キー, デフォルト値)
tz = request.args.get("tz", "UTC")
```

### TODO 3: タイムゾーンのバリデーション

**要件**:
- 取得したタイムゾーン `tz` が `ALLOWED_TZ` 辞書に含まれているか確認
- 含まれていない場合、HTTPステータス 400 で `"INVALID_TIMEZONE"` エラーを返す

**検証方法**:
```python
if tz not in ALLOWED_TZ:
    return error_response
```

### TODO 4: 現在時刻の取得

**要件**:
- `datetime.now()` に `ZoneInfo` を使用して、指定されたタイムゾーンの現在時刻を取得
- タイムゾーン名は `ALLOWED_TZ[tz]` から取得

**ZoneInfo の使い方**:
```python
from datetime import datetime
from zoneinfo import ZoneInfo

# タイムゾーンオブジェクトを作成
tz_obj = ZoneInfo("Asia/Tokyo")

# 指定タイムゾーンの現在時刻
now = datetime.now(tz_obj)
```

### TODO 5: レスポンスの作成

**要件**:
- `tz`: リクエストされたタイムゾーン名
- `iso`: `datetime.isoformat()` メソッドで取得
- `epoch_ms`: `datetime.timestamp()` を使用し、ミリ秒に変換（× 1000）

**datetime メソッド**:
```python
# ISO 8601形式の文字列を取得
iso_string = now.isoformat()
# → "2024-12-18T15:30:45.123456+09:00"

# Unixエポックからの秒数を取得
timestamp_seconds = now.timestamp()
# → 1702879845.123456

# ミリ秒に変換
timestamp_ms = int(timestamp_seconds * 1000)
# → 1702879845123
```

## 5. HTTPステータスコード

| コード | 意味 | 使用場面 |
|-------|------|---------|
| 200 | OK | 正常に処理された |
| 400 | Bad Request | 不正なリクエスト（無効なタイムゾーン） |

### 400 Bad Request の使い方

**400 Bad Request** は、クライアントのリクエストが不正な場合に使用します。

**例**:
- サポートされていないタイムゾーンを指定した
- 必須パラメータが不足している

**タイマー機能との違い**:
- タイマー: 409 Conflict（状態の矛盾）
- 世界時計: 400 Bad Request（入力エラー）

## 6. 使用例

### シナリオ1: デフォルト（UTC）

```bash
curl http://localhost:5050/clock
# → {
#     "tz": "UTC",
#     "iso": "2024-12-18T06:30:45.123456+00:00",
#     "epoch_ms": 1702879845123
#    }
```

### シナリオ2: 東京時刻

```bash
curl "http://localhost:5050/clock?tz=Asia/Tokyo"
# → {
#     "tz": "Asia/Tokyo",
#     "iso": "2024-12-18T15:30:45.123456+09:00",
#     "epoch_ms": 1702879845123
#    }
```

### シナリオ3: ニューヨーク時刻

```bash
curl "http://localhost:5050/clock?tz=America/New_York"
# → {
#     "tz": "America/New_York",
#     "iso": "2024-12-18T01:30:45.123456-05:00",
#     "epoch_ms": 1702879845123
#    }
```

### シナリオ4: エラーケース

```bash
curl "http://localhost:5050/clock?tz=Invalid/Timezone"
# → {"error": "INVALID_TIMEZONE"}
# HTTPステータス: 400 Bad Request
```

## 7. タイムゾーンについて

### IANA タイムゾーンデータベース

- **正式名称**: Internet Assigned Numbers Authority (IANA) Time Zone Database
- **形式**: `地域/都市` （例: `Asia/Tokyo`）
- **特徴**: 夏時間（DST）の自動処理

### Python の ZoneInfo（Python 3.9+）

```python
from zoneinfo import ZoneInfo

# タイムゾーンオブジェクトを作成
tokyo = ZoneInfo("Asia/Tokyo")

# 使用例
now_tokyo = datetime.now(tokyo)
```

### ISO 8601 形式

```
2024-12-18T15:30:45.123456+09:00
└─ 日付 ─┘ └─ 時刻 ─┘ └─ タイムゾーン
```

- **日付**: YYYY-MM-DD
- **時刻**: HH:MM:SS.ffffff
- **タイムゾーン**: +HH:MM または -HH:MM（UTCとの時差）

---

# 補足情報

## グローバル変数の扱い

Python では、関数内でグローバル変数を**変更**する場合、`global` 宣言が必要です。

```python
# グローバル変数
state = "stopped"

def start_timer():
    global state  # これが必要
    state = "running"  # 変更

def get_timer():
    # 読み取りだけなら global 不要
    return state
```

## 単位変換

### 時間の単位

| 単位 | 値 |
|------|-----|
| 1秒 | 1,000ミリ秒 |
| 1ミリ秒 | 0.001秒 |

### 変換式

```python
# 秒 → ミリ秒
milliseconds = seconds * 1000

# ミリ秒 → 秒
seconds = milliseconds / 1000
```

## エラーハンドリングのベストプラクティス

### 1. 適切なHTTPステータスコードを使用

- **200 OK**: 成功
- **400 Bad Request**: クライアントのリクエストが不正
- **409 Conflict**: リソースの状態が矛盾

### 2. 明確なエラーメッセージ

```json
{
  "error": "ALREADY_RUNNING"
}
```

- 大文字スネークケース
- 簡潔で明確
- エラーの原因が分かる

### 3. 早期リターン

```python
# エラーチェックを先に行う
if error_condition:
    return error_response

# 正常処理
# ...
return success_response
```

---

この仕様書に基づいて、穴埋め実装を進めてください。
