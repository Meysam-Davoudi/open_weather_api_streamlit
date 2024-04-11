import time
import random
import requests
from datetime import datetime, timezone
from PostgreSQLConnector import PostgreSQLConnector

db = PostgreSQLConnector()
open_weather_api_key = "4b3677480ec74a10854599ecf82f79f6"


def timestamp_to_string(unix_timestamp, datetime_format="%Y/%m/%d H:i:s"):
    date_obj = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
    date_string = date_obj.strftime(datetime_format)

    return date_string


def meters_to_km(meters):
    if meters >= 1000:
        km = meters / 1000
        return f"{km} km"
    else:
        return f"{meters} m"


def check_requirements():
    db.connect()

    if not (db.table_exists("countries") and
            db.table_exists("cities") and
            db.table_exists("weather")):
        db.execute_sql_file("requirements.sql")
        insert_db_countries_and_cities()

    db.disconnect()


def insert_db_countries_and_cities():
    url = "https://countriesnow.space/api/v0.1/countries"
    response = requests.get(url)
    countries_json = response.json()

    db.connect()

    for country in countries_json["data"]:
        if country['iso3'] != "ISR":
            country_dict = {'name': country['country'], 'iso2': country['iso2'], 'iso3': country['iso3']}
            country_id = db.insert('countries', country_dict)

            random_cities = random.sample(country['cities'], k=min(5, len(country['cities'])))

            for city in random_cities:
                city_dict = {'city_name': city, 'country_id': country_id}
                db.insert('cities', city_dict)

    db.disconnect()


def get_country_city_list():
    db.connect()
    cities = db.execute_query("""
    SELECT cities.id AS city_id, cities.city_name, countries.name AS country_name, countries.iso2 AS country_iso
    FROM cities
    JOIN countries ON cities.country_id = countries.id;
    """)
    db.disconnect()

    return cities


def get_lat_lon(city_id, city_name, country_iso2):
    result = [0, 0]

    db.connect()
    lat_lon = db.select(table="cities", columns=["lat", "lon"], condition="id = %s", parameters=[city_id])

    if any(item is None for item in lat_lon[0]):
        base_url = "http://api.openweathermap.org/geo/1.0/direct"
        parameters = {
            "q": f"{city_name},{country_iso2}",
            "appid": open_weather_api_key,
        }

        response = requests.get(url=base_url, params=parameters).json()
        if response:
            db.update(table="cities", values={"lat": response[0]['lat'], "lon": response[0]['lon']},
                      condition="id = %s", parameters=[city_id])
            result = [response[0]['lat'], response[0]['lon']]

        time.sleep(random.uniform(1, 2))

    else:
        result = [lat_lon[0][0], lat_lon[0][1]]

    db.disconnect()

    return result


def get_weather_status(location, forecast_type="24 Hours"):
    weather_base_url = "https://api.openweathermap.org/data/2.5/forecast"

    lat, lon = get_lat_lon(location[0], location[1], location[3])

    weather_parameters = {
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "appid": open_weather_api_key,
    }

    data = {}
    response = requests.get(url=weather_base_url, params=weather_parameters).json()

    if response["cod"] == "200":

        forecast_index = 8 + 1 if forecast_type == "24 Hours" else 8 * 5

        c = 1
        for forecast in response["list"]:
            if c == forecast_index:
                data = {
                    'city_id': location[0],
                    'forecast_type': forecast_type,
                    'temperature': forecast['main']['temp'],
                    'pressure': forecast['main']['pressure'],
                    'humidity': forecast['main']['humidity'],
                    'visibility': forecast['visibility']
                }
                db.connect()
                db.insert('weather', data)
                db.disconnect()

                data["description"] = forecast['weather'][0]['description']
                data["date"] = forecast['dt_txt']
                data["image_url"] = f"https://openweathermap.org/img/w/{forecast['weather'][0]['icon']}.png"

                break

            c += 1

    return data


def weather_card_html_layout(weather_status=None):
    result_html_layout = ""

    if weather_status:
        result_html_layout += f'''
                        <div style="border: 2px solid #e6e6e6; border-radius: 5px; margin-top:30px; padding: 10px;;
                                    text-align:center; float:left">
                            <img src="{weather_status["image_url"]}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%;">
                            <h2 style="margin-top: 10px; margin-bottom: 5px;color:purple">{weather_status["temperature"]}°C</h2>
                            <p style="margin-top: 10px; margin-bottom: 5px;">Pressure: {weather_status["pressure"]}hPa</p>
                            <p style="margin-top: 10px; margin-bottom: 5px;">Humidity: {weather_status["humidity"]}%</p>
                            <p style="margin-top: 10px; margin-bottom: 5px;">Visibility: {meters_to_km(weather_status["visibility"])}</p> 
                            <p style="margin-top: 0; margin-bottom: 10px;font-weight:bold">{weather_status["description"]}</p>
                            <p style="margin-top: 0; margin-bottom: 10px;font-weight:bold;color:blue">{weather_status["date"].replace('-', '/')}</p>
                        </div>
                        '''

    return result_html_layout


def get_requests_history():
    db.connect()
    result = db.execute_query("""
        SELECT
                weather.*,
                countries.name AS country_name,
                cities.city_name
            FROM
                weather
            JOIN
                cities ON weather.city_id = cities.id
            JOIN
                countries ON cities.country_id = countries.id
        """)
    db.disconnect()

    return result


def delete_request_history(id):
    db.connect()
    db.delete("weather", condition="id = %s", parameters=[id])
    db.disconnect()


def clear_requests_history():
    db.connect()
    db.delete("weather")
    db.disconnect()
