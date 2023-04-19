from flask import Flask, render_template, request, jsonify 
import os
import openai
from datetime import date, timedelta, datetime
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

# New route to generate output from a generated calendar
@app.route('/generate_output', methods=['POST'])
def generate_output():
    # Get the generated calendar from the request body
    generated_calendar = request.json['generated_calendar']
    
    # Call the OpenAI API to generate output using the generated calendar
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Use the following generated calendar as input to generate a new schedule that is written in .ics format:\n{generated_calendar}\n. It should follow this format UID:1 DTSTART;VALUE=DATE-TIME:20230417T063000, DTEND;VALUE=DATE-TIME:20230417T064500, SUMMARY:Wake up & Morning routine, END:VEVENT. This format needs to be able to able to be imported into my google calendar. Each activity should be the summary field in the .ics format.",
            temperature=0.5,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_output = response.choices[0].text.strip()
        print("Generated Output:", generated_output)  # Log the generated output
    
    except Exception as e:
        return jsonify({"error": str(e)})

    return jsonify({"output": generated_output})

@app.route('/generate_event_details', methods=['POST'])
def generate_event_details():
    # Get the event details from the form data submitted by the user
    event_details = request.form.get('event_details')
    
    # Call the OpenAI API to generate the event details
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Use the information from {event_details} to generate schedule that can be imported into google calendar. It should be created in the following format: BEGIN:VCALENDAR, VERSION:2.0, PRODID:-//Your Schedule//EN, BEGIN:VEVENT, UID:1, DTSTART;VALUE=DATE-TIME:20230417T063000, DTEND;VALUE=DATE-TIME:20230417T064500, SUMMARY:Wake up & Morning routine, END:VEVENT, END:VCALENDAR",
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_event_details = response.choices[0].text.strip()
        print("Generated Event Details:", generated_event_details)  # Log the generated event details
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
    return jsonify({"event_details": generated_event_details})

if __name__ == '__main__':
    app.run(debug=False)
