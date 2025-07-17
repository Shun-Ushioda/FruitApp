from flask import Flask, render_template, request, url_for
import google.generativeai as genai
import requests
import os
import random
from datetime import datetime

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

if not GOOGLE_API_KEY or not PIXABAY_API_KEY:
    raise RuntimeError("APIキーが設定されていません")

genai.configure(api_key=GOOGLE_API_KEY)

# Geminiモデル
SYSTEM_PROMPT = (
    "あなたはフルーツの専門家です。"
    "入力された果物に対して、特徴・味・旬・栄養・豆知識などを、"
    "日本語で200文字以内でやさしく紹介してください。"
)
model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=[SYSTEM_PROMPT])

# フルーツ紹介
def get_fruit_description(name):
    chat = model.start_chat(history=[])
    prompt = f"フルーツの名前：{name}"
    response = chat.send_message(prompt)
    return response.text.strip()

# 一言コメント（ウッシー）
def get_ussy_comment(fruit):
    prompt = (
        "あなたは潮田駿の分身です。天然でちょっと知的なキャラ“ウッシー”として、"
        f"「{fruit}」に対する一言コメントを20〜50文字で書いてください。"
        "自分のことは「僕」と呼んでいます。パフェが大好きです。"

    )
    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)
    return response.text.strip()

# Pixabay画像取得
def get_fruit_image_url(name):
    endpoint = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": f"{name} フルーツ",
        "image_type": "photo",
        "lang": "ja",
        "per_page": 3
    }
    res = requests.get(endpoint, params=params)
    data = res.json()
    if "hits" in data and len(data["hits"]) > 0:
        return data["hits"][0]["webformatURL"]
    else:
        return url_for("static", filename="default_fruit.jpg")

# 季節のおすすめ
def get_seasonal_fruit():
    month = datetime.now().month
    seasonal = {
        1: ["いちご", "みかん", "りんご", "キウイ"],
        2: ["いちご", "キウイ", "デコポン", "はっさく"],
        3: ["いちご", "文旦", "清見オレンジ", "キウイ"],
        4: ["びわ", "グレープフルーツ", "清見オレンジ", "パイナップル"],
        5: ["さくらんぼ", "マンゴー", "メロン", "びわ"],
        6: ["マンゴー", "メロン", "あんず", "さくらんぼ"],
        7: ["すいか", "ブルーベリー", "もも", "パッションフルーツ"],
        8: ["すいか", "ぶどう", "もも", "いちじく"],
        9: ["ぶどう", "なし", "いちじく", "りんご"],
        10: ["りんご", "かき", "ぶどう", "くり"],
        11: ["りんご", "みかん", "かき", "ゆず"],
        12: ["みかん", "いちご", "ゆず", "りんご"]
    }
    return random.choice(seasonal.get(month, ["りんご"]))

# ルート
@app.route("/", methods=["GET", "POST"])
def index():
    fruit = ""
    description = ""
    image_url = ""
    ussy_comment = ""
    seasonal_fruit = get_seasonal_fruit()

    if request.method == "POST":
        fruit = request.form["fruit"].strip()
        if fruit:
            print(f"get_fruit: {fruit}")
            description = get_fruit_description(fruit)
            image_url = get_fruit_image_url(fruit)
            ussy_comment = get_ussy_comment(fruit)

    return render_template("index.html",
                           fruit=fruit,
                           description=description,
                           image_url=image_url,
                           seasonal_fruit=seasonal_fruit,
                           ussy_comment=ussy_comment)

if __name__ == "__main__":
    app.run(debug=True)