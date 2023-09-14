1. Install the requirements.txt file, then cd into PlanerAI
2. Place your Google API key in the views.py file (You can create your own .env if you'd like, but for testing purposes it might just be best to directly place it on the variable)
2. `python manage.py migrate`
2. `python manage.py runserver`
3. `python manage.py test`

Example call: http://localhost:8000/forecasts?city=Berlin