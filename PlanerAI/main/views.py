import requests
import json
from django.http import HttpResponse, QueryDict


def forecasts(request):
    # Place API key here
    api_key = None
    city_name = request.GET.get('city', 'berlin')
    geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
    geocoding_response = requests.get(geocoding_url)
    data = geocoding_response.json()

    if geocoding_response.status_code != 200:
        return HttpResponse(data["status"])

    location = data["results"][0]["geometry"]["location"]
    latitude = location["lat"]
    longitude = location["lng"]
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,rain_sum,windspeed_10m_max&timezone=GMT&models=best_match"
    forecast_response = requests.get(forecast_url)

    if forecast_response.status_code != 200:
        return HttpResponse(forecast_response.status_code)

    data = forecast_response.json()

    daily = data.get("daily", {})
    days = daily.get("time", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    rain = daily.get("rain_sum", [])
    wind_speed = daily.get("windspeed_10m_max")

    return_data = {}
    for i, day in enumerate(days):
        day_data = {}
        day_data["temp_max"] = temp_max[i]
        day_data["temp_min"] = temp_min[i]
        day_data["rain"] = rain[i]
        day_data["wind_speed"] = wind_speed[i]

        classification = "sunny"
        if rain[i] >= 5:
            if wind_speed[i] >= 50:
                classification = "stormy"
            else:
                classification = "rainy"
        elif wind_speed[i] >= 50:
            if rain[i] >= 5:
                classification = "stormy"
            else:
                classification = "windy"
        day_data["classification"] = classification

        return_data[day] = day_data
    json_return_data = json.dumps(return_data)

    return HttpResponse(json_return_data)

