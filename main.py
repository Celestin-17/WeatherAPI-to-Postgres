from twilio.rest import Client
from credentials import *
import datetime as dt
import requests
import psycopg2
import pandas
import smtplib

fetched_data = None
rainAlert = False
forecast = {}
city = ""
avg_temp = 0
avg_h = 0
avg_w = 0
lat = 0
long = 0

time = dt.datetime.now()
t_hour = time.hour
t_day = time.day
t_month = time.month
t_year = time.year
t_month = str(t_month).zfill(2)
t_day = str(t_day).zfill(2)
t_hour = str(t_hour).zfill(2)
fdate = f"{t_year}-{t_month}-{t_day} {t_hour}"

def city_check(city: str):
    global lat, long
    geocoder_params = {
        "q": city,
        "appid": APPID
    }
    try:
        with requests.get(url=geocoder_endpoint, params=geocoder_params) as response:
            response.raise_for_status()
            data = response.json()
            lat = round(data[0]["lat"], 2)
            long = round(data[0]["lon"], 2)
            if (lat == 0 and long == 0):
                print(f"We can't find the coordinates for {city} !")
            else:
                city_params = {
                    "lat": lat,
                    "lon": long,
                    "cnt": "4",
                    "appid": APPID
                }
                with requests.get(url=weatherAPI_endpoint, params=city_params) as response:
                    response.raise_for_status()
                    data = response.json()
                    city_weather = []
                    for element in data["list"]:
                        status = {
                            "Interval": element["dt_txt"][5:],
                            "Sky": element["weather"][0]["main"],
                            "Windspeed": str(element["wind"]["speed"]) + " Km/h",
                            "Humidity": str(element["main"]["humidity"]) + " %",
                            "Temperature": str(round(element["main"]["temp"] - 273.15, 1)) + " °C"
                        }
                        city_weather.append(status)
                    df = pandas.DataFrame(city_weather)
                    print(f"\nThere is the forecast for the city: {city.capitalize()}\n")
                    print(df)
    except Exception as e:
        print(f"\nWe can't find the forecast for the city: {city}\n")

def rain_alert():
    global target_number, base_number
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(MY_EMAIL, MY_EMAIL, msg="Subject:Rain alert!\n\nIt's forecasted to rain !")
    client = Client(account_sid, auth_token)
    message = client.messages.create(body="Rain Alert - It's going to rain !", from_=base_number, to=target_number)

def update(): # Updates the db with the weather forecast data if available
    global rainAlert, fdate
    response = requests.get(url=weatherAPI_endpoint, params=weatherAPI_params)
    response.raise_for_status()
    data = response.json()
    weather_data = []

    for element in data["list"]:
        weather_status = {
            "weather_id" : element["weather"][0]["id"],
            "weather_time" : element["dt_txt"],
            "weather_main" : element["weather"][0]["main"],
            "weather_windspeed" : element["wind"]["speed"],
            "weather_humidity" : element["main"]["humidity"],
            "weather_temp" : element["main"]["temp"] - 273.15
        }
        weather_data.append(weather_status)
    response.close()

    try:
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor() as cursor:
                check_query = f"""SELECT COUNT(*) FROM weatherTable WHERE date >= '{fdate}';"""
                print("Checking db for existing forecast...")
                cursor.execute(check_query)
                data = cursor.fetchone()
                rows = data[0]
                if rows > 0:
                    print("Forecast already updated into db\n\n")
                    return
                else:
                    n = 0
                    for element in weather_data:
                        if element["weather_main"] == "Rain":
                            rainAlert = True
                        update_query = f"""INSERT INTO weatherTable(date, main, weatherid, windspeed, humidity, temp) VALUES
                            ('{element["weather_time"]}', '{element["weather_main"]}', '{element["weather_id"]}',
                            '{element["weather_windspeed"]}', '{element["weather_humidity"]}', '{round(element["weather_temp"],2)}');
                            """
                        cursor.execute(update_query)
                        n += 1
                    print(f"DB updated with {n} entries !")
    except Exception as e:
        print("Exception:" + str(e))


def main():
    global rainAlert
    try:
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor() as cursor:
                query = (f"""SELECT * FROM weatherTable WHERE date >= '{fdate}' ORDER BY date; """)
                print(fdate)
                cursor.execute(query)
                data = cursor.fetchall()
                fetched_data = pandas.DataFrame(data)
                fetched_data = fetched_data.drop(columns=0, axis=1)
    except Exception as e:
        print(e)
    end = False
    while not end:
        choice = input("MENU: \nType '1' to see the forecast for Bucharest\nType '2' to see the forecast for any city\n"
        "Type '3' to check the database entries\nType 'exit' to terminate the program\n")
        if choice == "1":
            interval = [row[1] for index, row in fetched_data.iterrows()]
            temp_interval = [row[6] for index, row in fetched_data.iterrows()]
            h_interval = [row[5] for index, row in fetched_data.iterrows()]
            w_interval = [row[4] for index, row in fetched_data.iterrows()]
            code_interval = [row[3] for index, row in fetched_data.iterrows()]
            first_interval = interval[0]
            last_interval = interval[-1]
            avg_h = sum(h_interval) / len(h_interval)
            avg_w = sum(w_interval) / len(w_interval)
            avg_temp = sum(temp_interval) / len(temp_interval)
            for code in code_interval:
                if code == "Rain":
                    rainAlert = True
            today = f"{first_interval[8:10]}/{first_interval[5:7]}/{first_interval[:4]}"
            if len(interval) != 1:
                print(f"Available forecast for today ({today}):\nThe available interval is between {first_interval[11:]} and {last_interval[11:]}.")
            else:
                print(f"Available forecast for today ({today}):\nThe only available interval is: {interval[0][11:]}.")
            choice = input("Do you want to proceed with the weather forecast? Type 'yes' or 'no' \n")
            if choice == "yes":
                fetched_data = fetched_data.sort_values(by=2, ascending=False)
                weather_code = fetched_data[2].loc[fetched_data.index[0]]
                weather_status = fetched_data[3].loc[fetched_data.index[0]]
                print(f"Weather code: {weather_code} --- {weather_status}")
                print(f"Average temperature in the forecasted period is: {round(avg_temp, 1)}°C ")
                print(f"Average windspeed: {round(avg_w, 1)} km/h | Humidity: {round(avg_h, 2)}%")
                if rainAlert:
                    print(f"It's forecasted to rain !")
                choice = input("Do you want to restart the program? Type 'yes' or 'no'\n").lower()
                if choice == "no":
                    print("Terminating the program...")
                    break
            else:
                print("Terminating the program...")
                break
        elif choice == "2":
            choice = input("Enter the name of the city: \n").lower()
            city_check(choice)
            end_game = input("Do you want to restart the program? Type 'yes' or 'no'\n").lower()
            if end_game == "no":
                print("Terminating the program...")
                return
        elif choice == "3":
            with psycopg2.connect(**connection_params) as connection:
                with connection.cursor() as cursor:
                    query = """SELECT * FROM weatherTable ORDER BY date DESC LIMIT 30;"""
                    cursor.execute(query)
                    data = cursor.fetchall()
                    df = pandas.DataFrame(data)
                    df = df.drop(0, axis=1)
                    df = df.drop(2, axis=1)
                    df = df.rename(columns={1:"Date",3:"Sky",4:"Windspeed",5:"Humidity",6:"Temperature"})
                    print(df)
                    choice = input("\nDo you want to restart the program? Type 'yes' or 'no'\n").lower()
                    if choice == "no":
                        print("Terminating the program...")
                        return
        elif choice == "exit":
            print("Terminating the program...")
            end = True

if __name__ == "__main__":
    update()
    main()