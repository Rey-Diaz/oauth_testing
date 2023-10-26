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
from config import WEBEX_CONFIG

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
    consumer_key=WEBEX_CONFIG['CONSUMER_KEY'],
    consumer_secret=WEBEX_CONFIG['CONSUMER_SECRET'],
    request_token_params={'scope': WEBEX_CONFIG['SCOPE']},
    base_url=WEBEX_CONFIG['BASE_URL'],
    request_token_url=None,
    access_token_method=WEBEX_CONFIG['ACCESS_TOKEN_METHOD'],
    access_token_url=WEBEX_CONFIG['ACCESS_TOKEN_URL'],
    authorize_url=WEBEX_CONFIG['AUTHORIZE_URL']
)

@app.route('/')
def index():
    logging.info("Serving the captive portal page.")
    return render_template_string(open("captive_portal.html").read())

@app.route('/login')
def login():
    logging.info("Initiating OAuth flow. Redirecting user to Webex for authentication...")
    oauth_redirect = webex.authorize(callback=WEBEX_CONFIG['REDIRECT_URI'])
    logging.debug(f"OAuth redirect URL: {oauth_redirect.location}")
    return oauth_redirect

@app.route('/login/authorized')
def authorized():
    logging.info("Received callback from Webex after OAuth authentication.")
    
    code = request.args.get('code')
    data = {
        'grant_type': WEBEX_CONFIG['GRANT_TYPE'],
        'client_id': WEBEX_CONFIG['CONSUMER_KEY'],
        'client_secret': WEBEX_CONFIG['CONSUMER_SECRET'],
        'code': code,
        'redirect_uri': WEBEX_CONFIG['REDIRECT_URI']
    }
    response = requests.post(WEBEX_CONFIG['ACCESS_TOKEN_URL'], data=data).json()
    
    logging.debug(f"Webex API response: {response}")

    if 'access_token' not in response:
        logging.error(f"Authentication failed. Full response: {response}")
        return 'Access denied: reason={} error={}'.format(
            response.get('error_reason', 'N/A'),
            response.get('error_description', 'N/A')
        )

    logging.info("Authentication successful. Storing access token in session.")
    session['webex_token'] = (response['access_token'], '')
    
    headers = {
        'Authorization': f"Bearer {response['access_token']}"
    }
    user_info = requests.get('https://webexapis.com/v1/me', headers=headers).json()
    logging.debug(f"User details: {user_info}")

    return 'Logged in successfully!'

@webex.tokengetter
def get_webex_oauth_token():
    # Retrieve the stored Webex OAuth token from the session
    return session.get('webex_token')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
