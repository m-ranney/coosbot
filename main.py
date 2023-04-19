from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import requests
import os
import openai
from datetime import date, timedelta
import json

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
      
        # Split the generated schedule into individual activities
        activities_list = generated_schedule.split("\n\n")
        activities_list = [activity.split("\n") for activity in activities_list]
    
        # Create a list of dictionaries with activity name, start time, and end time
        activities_dict_list = []
        for activity in activities_list:
            activity_dict = {}
            for i in range(len(activity)):
                if i == 0:
                    activity_dict["name"] = activity[i]
                elif "start time" in activity[i]:
                    activity_dict["start_time"] = activity[i].split(": ")[1]
                elif "end time" in activity[i]:
                    activity_dict["end_time"] = activity[i].split(": ")[1]
            activities_dict_list.append(activity_dict)
    
        # Create a table view with activity name, start time, and end time
        table = "<table><tr><th>Activity</th><th>Start Time</th><th>End Time</th></tr>"
        for activity in activities_dict_list:
            table += f"<tr><td>{activity['name']}</td><td>{activity['start_time']}</td><td>{activity['end_time']}</td></tr>"
        table += "</table>"
    
        return jsonify({"schedule": table})

  
if __name__ == '__main__':
    app.run(debug=False)
