from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock

class ForecastsViewTest(TestCase):
    @patch('PlanerAI.main.views.requests.get')
    def test_successful_forecast_request(self, mock_get):
        mock_geocoding_response = MagicMock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.json.return_value = {
            "results": [{
                "geometry": {"location": {"lat": 52.5200, "lng": 13.4050}}
            }]
        }
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            "daily": {
                "time": ["2023-09-15", "2023-09-16"],
                "temperature_2m_max": [25.0, 26.0],
                "temperature_2m_min": [15.0, 16.0],
                "rain_sum": [0.0, 5.0],
                "windspeed_10m_max": [10.0, 55.0]
            }
        }

        mock_get.side_effect = [mock_geocoding_response, mock_forecast_response]

        response = self.client.get(reverse('forecasts'), {'city': 'berlin'})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "2023-09-15": {
                "temp_max": 25.0,
                "temp_min": 15.0,
                "rain": 0.0,
                "wind_speed": 10.0,
                "classification": "sunny"
            },
            "2023-09-16": {
                "temp_max": 26.0,
                "temp_min": 16.0,
                "rain": 5.0,
                "wind_speed": 55.0,
                "classification": "stormy"
            }
        })

    @patch('PlanerAI.main.views.requests.get')
    def test_geocoding_failure(self, mock_get):
        mock_geocoding_response = MagicMock()
        mock_geocoding_response.status_code = 404
        mock_geocoding_response.json.return_value = {"status": "not_found"}
        mock_get.return_value = mock_geocoding_response

        response = self.client.get(reverse('forecasts'), {'city': 'non_existent_city'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"not_found")

    @patch('PlanerAI.main.views.requests.get')
    def test_forecast_failure(self, mock_get):
        mock_geocoding_response = MagicMock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.json.return_value = {
            "results": [{
                "geometry": {"location": {"lat": 52.5200, "lng": 13.4050}}
            }]
        }
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 404
        mock_get.side_effect = [mock_geocoding_response, mock_forecast_response]

        response = self.client.get(reverse('forecasts'), {'city': 'berlin'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"404")
