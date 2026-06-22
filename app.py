from flask import Flask, render_template, request, session, redirect, url_for
import requests
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret-key-demo"

API_KEY = os.getenv("API_KEY")

FREE_DAILY_LIMIT = 10   # batas pencarian/hari untuk plan Free
HISTORY_LIMIT = 5       # jumlah riwayat pencarian yang disimpan untuk plan Pro


# ---------- HELPERS ----------
def get_plan():
    return session.get("plan", "free")


def quota_status():
    """
    Free  -> dict berisi used/remaining/limit/percent untuk hari ini.
    Pro   -> None (unlimited, tidak ada yang perlu ditampilkan).
    """
    if get_plan() == "pro":
        return None

    today = date.today().isoformat()
    if session.get("quota_date") != today:
        session["quota_date"] = today
        session["quota_used"] = 0

    used = session.get("quota_used", 0)
    limit = FREE_DAILY_LIMIT
    return {
        "used": used,
        "remaining": max(limit - used, 0),
        "limit": limit,
        "percent": min(round(used / limit * 100), 100),
    }


def consume_quota():
    """Coba pakai satu kuota pencarian. Pro selalu boleh, Free dibatasi per hari."""
    if get_plan() == "pro":
        return True

    status = quota_status()
    if status["remaining"] <= 0:
        return False

    session["quota_used"] = status["used"] + 1
    return True


def add_to_history(entry):
    history = session.get("history", [])
    history.insert(0, entry)
    session["history"] = history[:HISTORY_LIMIT]


# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None
    plan = get_plan()

    if request.method == "POST":
        city = request.form.get("city")

        if not city:
            error = "Masukkan nama kota terlebih dahulu"
        elif not consume_quota():
            error = (
                f"Limit {FREE_DAILY_LIMIT} pencarian/hari untuk plan Free sudah tercapai. "
                "Upgrade ke Pro untuk pencarian unlimited."
            )
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=id"
            res = requests.get(url).json()

            if res.get("cod") == 200:
                data = {
                    "city": res["name"],
                    "country": res["sys"]["country"],
                    "temp": res["main"]["temp"],
                    "feels": res["main"]["feels_like"],
                    "humidity": res["main"]["humidity"],
                    "desc": res["weather"][0]["description"],
                    "wind": res["wind"]["speed"],
                }

                # ----- Fitur khusus Pro: detail lebih lengkap + riwayat -----
                if plan == "pro":
                    data["pressure"] = res["main"]["pressure"]
                    data["visibility"] = round(res.get("visibility", 0) / 1000, 1)
                    data["sunrise"] = datetime.fromtimestamp(res["sys"]["sunrise"]).strftime("%H:%M")
                    data["sunset"] = datetime.fromtimestamp(res["sys"]["sunset"]).strftime("%H:%M")

                    add_to_history({
                        "city": data["city"],
                        "country": data["country"],
                        "temp": data["temp"],
                        "desc": data["desc"],
                        "time": datetime.now().strftime("%d %b, %H:%M"),
                    })
            else:
                error = "Kota tidak ditemukan"

    return render_template(
        "index.html",
        data=data,
        error=error,
        plan=plan,
        quota=quota_status(),
    )


# ---------- PRICING ----------
@app.route("/pricing")
def pricing():
    return render_template("pricing.html", plan=get_plan(), limit=FREE_DAILY_LIMIT)


# ---------- SIMULASI BELI ----------
@app.route("/upgrade/<plan>")
def upgrade(plan):
    if plan not in ("free", "pro"):
        return redirect(url_for("pricing"))

    session["plan"] = plan
    if plan == "free":
        session.pop("history", None)  # riwayat adalah fitur Pro

    return redirect(url_for("pricing"))


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    plan = get_plan()
    return render_template(
        "dashboard.html",
        plan=plan,
        quota=quota_status(),
        history=session.get("history", []),
    )


if __name__ == "__main__":
    app.run(debug=True)