#Захист: https://youtu.be/fmKLhIE_7Tg
import os
import datetime
from pathlib import Path
import io

import requests
import numpy as np
import pandas as pd
from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    Response
)
from sklearn.linear_model import LinearRegression
import joblib

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change_this")
OW_KEY = os.getenv("OPENWEATHER_API_KEY", "bd5e378503939ddaee76f12ad7a97608")

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

def get_history_df(lat, lon, start, end):
    fmt = "%Y-%m-%d"
    ts_start = int(datetime.datetime.strptime(start, fmt).timestamp())
    ts_end   = int(datetime.datetime.strptime(end,   fmt).timestamp())
    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution/history",
        params={"lat": lat, "lon": lon, "start": ts_start, "end": ts_end, "appid": OW_KEY}
    )
    resp.raise_for_status()
    raw = resp.json().get("list", [])
    df = pd.DataFrame([{"dt": datetime.datetime.fromtimestamp(x["dt"]), **x["components"]} for x in raw])
    df = df[["dt", "pm2_5"]]
    df["pm2_5_norm"] = (df["pm2_5"] - df["pm2_5"].min()) / (df["pm2_5"].max() - df["pm2_5"].min())
    df["day"] = (df["dt"] - df["dt"].min()).dt.days.values.reshape(-1,1)
    return df

def compute_forecast(model, last_day, last_date, days=7):
    fmt = "%Y-%m-%d"
    forecast = []
    for i in range(1, days+1):
        d0 = last_date + datetime.timedelta(days=i)
        pred = round(model.predict(np.array([[last_day + i]]))[0], 2)
        forecast.append({"date": d0.strftime(fmt), "pm2_5": pred})
    return forecast

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = {}
    if request.method == "POST":
        try:
            lat = float(request.form["lat"])
            lon = float(request.form["lon"])
            start = request.form["start_date"]
            end = request.form["end_date"]
            df = get_history_df(lat, lon, start, end)

            # збереження параметрів для кнопки скачування
            result.update(lat=lat, lon=lon, start=start, end=end)

            # тренування / завантаження моделі
            X = df[["day"]].values
            y = df["pm2_5"].values
            model_path = MODEL_DIR / f"model_{lat}_{lon}.joblib"
            if model_path.exists():
                model = joblib.load(model_path)
            else:
                model = LinearRegression()
                model.fit(X, y)
                joblib.dump(model, model_path)

            last = int(df["day"].max())
            last_date = df["dt"].max()
            forecast = compute_forecast(model, last, last_date)

            # топ-5 міст
            cities = {
                "Kyiv": (50.45, 30.52),
                "Lviv": (49.84, 24.03),
                "Odesa": (46.48, 30.73),
                "Kharkiv": (49.99, 36.23),
                "Dnipro": (48.45, 35.05),
                "Zaporizhzhia": (47.84, 35.14),
                "Vinnytsia": (49.23, 28.47)
            }
            top = []
            for city, (clat, clon) in cities.items():
                r2 = requests.get(
                    "http://api.openweathermap.org/data/2.5/air_pollution",
                    params={"lat": clat, "lon": clon, "appid": OW_KEY}
                )
                r2.raise_for_status()
                pm = r2.json()["list"][0]["components"]["pm2_5"]
                top.append({"city": city, "pm2_5": pm})
            top5 = sorted(top, key=lambda x: -x["pm2_5"])[:5]

            result.update({
                "factors": ["pm2_5"],
                "history": df.to_dict("records"),
                "forecast": forecast,
                "top5": top5,
                "change": round(df["pm2_5"].iloc[-1] - df["pm2_5"].iloc[0], 2)
            })
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("analyze"))
    return render_template("analyze.html", result=result)

@app.route("/forecast", methods=["GET", "POST"])
def forecast_view():
    forecast = []
    if request.method == "POST":
        try:
            lat = float(request.form["lat"])
            lon = float(request.form["lon"])
            # використовуємо тільки останні 30 днів в історії
            end = datetime.date.today().strftime("%Y-%m-%d")
            start = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            df = get_history_df(lat, lon, start, end)
            X = df[["day"]].values
            y = df["pm2_5"].values
            model = LinearRegression().fit(X, y)
            last = int(df["day"].max())
            last_date = df["dt"].max()
            forecast = compute_forecast(model, last, last_date)
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("forecast_view"))
    return render_template("forecast.html", forecast=forecast)

@app.route("/download/history")
def download_history():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        start = request.args.get("start")
        end = request.args.get("end")
        df = get_history_df(lat, lon, start, end)
        csv_io = io.StringIO()
        df.to_csv(csv_io, index=False)
        csv_io.seek(0)
        return Response(
            csv_io.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=history.csv"}
        )
    except Exception as e:
        flash(f"Не вдалось згенерувати CSV: {e}", "danger")
        return redirect(url_for("analyze"))

@app.route("/map")
def map_view():

    cities = {
        "Kyiv": (50.45, 30.52),
        "Lviv": (49.84, 24.03),
        "Odesa": (46.48, 30.73),
        "Kharkiv": (49.99, 36.23),
        "Dnipro": (48.45, 35.05)
    }
    points = []
    for city, (clat, clon) in cities.items():
        r = requests.get(
            "http://api.openweathermap.org/data/2.5/air_pollution",
            params={"lat": clat, "lon": clon, "appid": OW_KEY}
        )
        r.raise_for_status()
        pm = r.json()["list"][0]["components"]["pm2_5"]
        points.append({"city": city, "lat": clat, "lon": clon, "val": pm})
    return render_template("map.html", points=points)

if __name__ == "__main__":
    app.run(debug=True)
