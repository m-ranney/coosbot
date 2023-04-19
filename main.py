from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import requests
import os
import openai
from datetime import date, timedelta, datetime
import json
import ics
from ics import Calendar, Event
from pytz import timezone

app = Flask(__name__)
app.secret_key = os.urandom(24)

my_secret = os.environ['OPENAI_API_KEY']
openai.api_key = my_secret

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

@app.route('/generate_calendar', methods=['POST'])
def generate_calendar():
    activities = request.form.get('activities')
    event_date = request.form.get('date')
    
    # Call the OpenAI API to generate the schedule
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Create a calendar schedule for the following activities on {event_date}:\n{activities}\n The calendar should include normal everyday activities even if they are not mentioned, like eating breakfast, lunch and dinner. It should not include going to work, because I work from home. Prioritize more time spent on work related activities and less time on liesure related activities. And a normal weekday schedule should begin at 6 am and end at 10 pm PT. A normal weekend schedule should begin at 7 am and end at 11 pm PT. Each activity should include the activity name and a start and end time with no overlapping activities.",
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_schedule = response.choices[0].text.strip()
        print("Generated Schedule:", generated_schedule)  # Log the generated schedule
    
    except Exception as e:
        return jsonify({"error": str(e)})

    return jsonify({"schedule": generated_schedule})

@app.route('/generate_ics', methods=['POST'])
def generate_ics():
    # Get the generated schedule from the request body
    schedule = request.json['schedule']
    
    # Create a new calendar
    cal = Calendar()

    # Call the OpenAI API to generate the schedule
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Create an calendar schedule in .ics format for {schedule}",
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_ics = response.choices[0].text.strip()
        print("Generated ICS Schedule:", generated_ics)  # Log the generated ics schedule
    
    except Exception as e:
        return jsonify({"error": str(e)})

    return jsonify({"ics_schedule": generated_ics})

if __name__ == '__main__':
    app.run(debug=False)
