 - WeatherAPI to Postgres DB -

The update() function retrieves 12h forecast data from openweathermap, checks the postgres db existing data and updates with the proceeding forecast.
The rain_alert() function is triggered when rain is forecasted and an Email/SMS alert is sent to the email and target number that've been set in the .env file

The program has 3 options:
1. First menu option checks the db for available forecast data for Bucharest from withing the time of the program execution.
   It returns the average for temperature, windspeed, humidity and triggers rain_alert() if rain's forecasted.
2. In the second you can check the available forecast for any city and it returns all the available forecast intervals giving you if forecasted a rain alert  without triggering the function.
3. Returns all the data entries from the postgres db.
