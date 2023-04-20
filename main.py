from flask import Flask, render_template, request, jsonify, send_from_directory 
import os
import openai
import uuid
import datetime
from datetime import date, datetime, timedelta
import re
import pytz
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


app = Flask(__name__)
app.secret_key = os.urandom(24)

my_secret = os.environ['OPENAI_API_KEY']
openai.api_key = my_secret

cal_secret = os.environ['GOOGLE_CAL_CLIENT_SECRET']
client_id = os.environ['GOOGLE_CAL_CLIENT_ID']
refresh_token = os.environ['GOOGLE_CAL_REFRESH_TOKEN']

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


@app.route('/add_event')
def add_event():
    return render_template('add_event.html')


# Set up OAuth 2.0
flow = InstalledAppFlow.from_client_config(
    client_config={
        "installed": {
            "client_id": client_id,
            "client_secret": cal_secret,
            "redirect_uris": ["https://coosbot.herokuapp.com/oauth2callback"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/calendar"],
)

credentials = flow.run_local_server(port=8080)

# Access the Google Calendar API
calendar_service = build("calendar", "v3", credentials=credentials)


@app.route('/get_client_data')
def get_client_data():
    return jsonify({"client_id": client_id, "cal_secret": cal_secret})


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
    today = date.today().strftime("%Y%m%d")

    # Call the OpenAI API to generate the event details
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Use the information from '{event_details}' to generate an event that can be imported into Google Calendar. Assume that today is {today}. Parse the event date, start time, and duration from the user input, and generate the event details in JSON format: '{{\"summary\": \"Example Event\", \"date\": \"20230417\", \"start_time\": \"063000\", \"end_time\": \"064500\"}}'.",
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_event_details = json.loads(response.choices[0].text.strip())
        print("Generated Event Details:", generated_event_details)  # Log the generated event details

        date_match = re.search(r"DTSTART;VALUE=DATE-TIME:(\d{8})", generated_event_details)
        start_time_match = re.search(r"DTSTART;VALUE=DATE-TIME:\d{8}T(\d{6})", generated_event_details)
        end_time_match = re.search(r"DTEND;VALUE=DATE-TIME:\d{8}T(\d{6})", generated_event_details)
    
        event_date = datetime.strptime(generated_event_details["date"], "%Y%m%d").strftime("%Y-%m-%d")
        event_start_time = generated_event_details["start_time"]
        event_end_time = generated_event_details["end_time"]
  
    except Exception as e:
        return jsonify({"error": str(e)})
    
    return jsonify({"generated_event_details": generated_event_details, "event_date": event_date, "event_start_time": event_start_time, "event_end_time": event_end_time})


def get_google_calendar_service():
    creds = Credentials.from_authorized_user_info(info={
        'client_id': client_id,
        'client_secret': cal_secret,
        'refresh_token': refresh_token,
        'token_uri': 'https://oauth2.googleapis.com/token'
    })

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
