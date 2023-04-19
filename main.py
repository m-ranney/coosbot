from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import openai
from datetime import date, timedelta

app = Flask(__name__)

openai_api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Define your routes here
@app.route('/')
def home():
    return render_template('home.html')

# More routes for other actions
@app.route('/calendar')
def calendar():
    tomorrow = date.today() + timedelta(days=1)
    default_date = tomorrow.isoformat()
    return render_template('calendar.html', default_date=default_date)
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)