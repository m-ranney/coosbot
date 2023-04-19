from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import openai
from datetime import date, timedelta
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

openai_api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Setup for calendar form entry
@app.route('/calendar')
def calendar():
    tomorrow = date.today() + timedelta(days=1)
    default_date = tomorrow.isoformat()
    return render_template('calendar.html', default_date=default_date)

# Generating the calendar route
@app.route('/generate_calendar', methods=['POST'])
def generate_calendar():
    activities = request.form.get('activities')
    event_date = request.form.get('date')
    
    # Call the OpenAI API to generate the schedule
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Create a calendar schedule for the following activities on {event_date}:\n{activities}\n The calendar should include normal everyday activities even if they are not mentioned, like eating breakfast, lunch and dinner. And a normal weekday schedule should begin at 6 am and end at 10 pm PT. A normal weekend schedule should begin at 7 am and end at 11 pm PT",
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_schedule = response.choices[0].text.strip()
    except Exception as e:
        flash("Error generating calendar schedule: " + str(e))
        return redirect(url_for('calendar'))

    return render_template('schedule_preview.html', schedule=generated_schedule)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)