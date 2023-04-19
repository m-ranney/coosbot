from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Define your routes here
@app.route('/')
def home():
    return render_template('home.html')

# More routes for other actions

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)