from flask import Flask, render_template, url_for, jsonify, request
import requests


app = Flask(__name__)

api_key = "59d3cbce5f4190ce077ab061f6c720fb"


def get_weather_emoji(weather_id):

    if 200 <= weather_id <= 232:
        return "⛈️"
    elif 300 <= weather_id <= 321:
        return "☁️"
    elif 500 <= weather_id <= 531:
        return "🌧️"
    elif 600 <= weather_id <= 622:
        return "❄️"
    elif 701 <= weather_id <= 741:
        return "🌫️"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "💨"
    elif weather_id == 781:
        return "🌪️"
    elif weather_id == 800:
        return "☀️"
    elif 801 <= weather_id <= 804:
        return "☁️"
    else:
        return ""


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None

    if request.method == "POST":
        city = request.form.get("city")
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        )
        data = request.get(url).json()
        if data["cod"] == 200:
            temp_c = data["main"]["temp"] - 273.15

            weather = {
                "city": city,
                "temperature": f"{temp_c:.1f}°C",
                "description": data["weather"][0]["description"].title(),
                "emoji": get_weather_emoji(data["weather"][0]["id"]),
            }
        else:
            weather = {"error": "City not found"}

    return render_template("weather.html", weatehr=weather)


@app.route("/weather")
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City is required"}), 400
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        feels_like = data["main"]["feels_like"] - 273.15
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather_id = data["weather"][0]["id"]
        result = {
            "city": city,
            "country": data["sys"]["country"],
            "temperature_k": temperature_k,
            "temperature_c": f"{temperature_c}",
            "weather_description": data["weather"][0]["description"].title(),
            "weather_id": weather_id,
            "temp": f"{temperature_c:.1f}°C",
            "emoji": get_weather_emoji(weather_id),
            "feels_like": round(feels_like, 1),
            "humidity": humidity,
            "wind_speed": wind_speed,
        }
        return jsonify(result)
    except requests.exceptions.HTTPError as http_error:
        match response.status_code:
            case 400:
                return jsonify({"error": "Bad requests"})
            case 401:
                return jsonify({"error": "Unauthorized\nInvalid API key"})
            case 403:
                return jsonify({"error": "Forbidden\nAccess is denied"})
            case 404:
                return jsonify({"error": "Not found\nCity not found"})
            case 500:
                return jsonify(
                    {"error": "Internal server error\nPlease try again later"}
                )
            case 502:
                return jsonify(
                    {"error": "Bad Gateway\nInvalid responde from the server"}
                )
            case 503:
                return jsonify({"error": "Service Unavailable\nServer is down"})
            case 504:
                return jsonify(
                    {"error": "Gateway Tiemout\nNo response from the server"}
                )
            case _:
                return jsonify({"error": f"HTTP error occured\n{http_error}"})

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection Error:\nCheck your internet connection"})
    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout Error:\nThe requests timed out"})
    except requests.exceptions.TooManyRedirects:
        # there was an ambiguous exception that occurred whike handling your requests
        return jsonify({"error": "Too many Redirects:\nCheck the URL"})
    except requests.exceptions.RequestException as req_error:
        return jsonify({"error": f"Request Error:\n{req_error}"})

    return render_template("weather.html")


if __name__ == "__main__":
    app.run(debug=True)
