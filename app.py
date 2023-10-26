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

# Initialize Flask application
app = Flask(__name__)
app.secret_key = '1234'  # Set a secret key for Flask sessions. Change this to a secure random value.

# Initialize OAuth for Flask
oauth = OAuth(app)

# Define Webex OAuth configuration
webex = oauth.remote_app(
    'webex',
    consumer_key='C4fbcf5b9c6a3cee01b8079fffff52c03d4d2b6e8d7338881b7993318fc639d7e',  # Webex OAuth client ID
    consumer_secret='dd39b9daae5adb1c7a9759683858c83f92fa2e8e183bdfcd0af6019e0ba83571',  # Webex OAuth client secret
    request_token_params={'scope': 'spark:all spark:kms'},  # OAuth scopes for Webex
    base_url='https://api.ciscospark.com/v1/',  # Base URL for Webex
    request_token_url=None,  # No request token URL for OAuth 2.0
    access_token_method='POST',  # HTTP method for obtaining access token
    access_token_url='https://api.ciscospark.com/v1/access_token',  # URL to obtain access token
    authorize_url='https://api.ciscospark.com/v1/authorize'  # URL for authorization
)

@app.route('/')
def index():
    # Render the captive portal page
    return render_template_string(open("captive_portal.html").read())

@app.route('/login')
def login():
    # Redirect user to Webex for OAuth authentication
    return webex.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    # Handle the callback after Webex OAuth authentication
    response = webex.authorized_response()
    
    # Check if the authentication was successful
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    # Store the access token in the session
    session['webex_token'] = (response['access_token'], '')
    
    # Here, you can use the access token to make authorized requests to Webex API.
    # For example, to get user details:
    headers = {
        'Authorization': f"Bearer {response['access_token']}"
    }
    user_info = requests.get('https://api.ciscospark.com/v1/me', headers=headers).json()
    print(user_info)  # Print user details for debugging

    return 'Logged in successfully!'

@webex.tokengetter
def get_webex_oauth_token():
    # Retrieve the stored Webex OAuth token from the session
    return session.get('webex_token')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
