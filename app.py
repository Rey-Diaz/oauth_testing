""" Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied."""

# Import necessary libraries and modules
from flask import Flask, redirect, request, render_template_string, session, url_for
from flask_oauthlib.client import OAuth
import requests
import logging

# Initialize Flask application
app = Flask(__name__)
app.secret_key = '1234'  # Set a secret key for Flask sessions. Change this to a secure random value.

# Initialize OAuth for Flask
oauth = OAuth(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define Webex OAuth configuration
webex = oauth.remote_app(
    'webex',
    consumer_key='C4fbcf5b9c6a3cee01b8079fffff52c03d4d2b6e8d7338881b7993318fc639d7e',  # Webex OAuth client ID
    consumer_secret='dd39b9daae5adb1c7a9759683858c83f92fa2e8e183bdfcd0af6019e0ba83571',  # Webex OAuth client secret
    request_token_params={'scope': 'spark:all spark:kms'},  # OAuth scopes for Webex
    base_url='https://webexapis.com/v1/',  # Base URL for Webex
    request_token_url=None,  # No request token URL for OAuth 2.0
    access_token_method='POST',  # HTTP method for obtaining access token
    access_token_url='https://webexapis.com/v1/access_token',
    authorize_url='https://webexapis.com/v1/authorize'
)

@app.route('/')
def index():
    # Render the captive portal page
    return render_template_string(open("captive_portal.html").read())

@app.route('/login')
def login():
    logging.info("Redirecting user to Webex for OAuth authentication...")
    return webex.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    logging.info("Received callback from Webex after OAuth authentication.")
    response = webex.authorized_response()
    
    if response is None or response.get('access_token') is None:
        logging.error(f"Authentication failed. Reason: {request.args['error_reason']}, Error: {request.args['error_description']}")
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    logging.info("Authentication successful. Storing access token in session.")
    session['webex_token'] = (response['access_token'], '')
    
    headers = {
        'Authorization': f"Bearer {response['access_token']}"
    }
    user_info = requests.get('https://api.ciscospark.com/v1/me', headers=headers).json()
    logging.debug(f"User details: {user_info}")

    return 'Logged in successfully!'

@webex.tokengetter
def get_webex_oauth_token():
    # Retrieve the stored Webex OAuth token from the session
    return session.get('webex_token')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
