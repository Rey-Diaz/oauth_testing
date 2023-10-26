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
    request_token_params={'scope': 'spark:all spark:kms'},# OAuth scopes for Webex
    base_url='https://api.ciscospark.com/v1/',  # Base URL for Webex
    request_token_url=None,  # No request token URL for OAuth 2.0
    access_token_method='POST',  # HTTP method for obtaining access token
    access_token_url='https://api.ciscospark.com/v1/access_token',  # URL to obtain access token
    authorize_url='https://api.ciscospark.com/v1/authorized'  # URL for authorization
)

# Define Meraki API key and network ID
MERAKI_API_KEY = '91827e9abc34e868af813bb69ce997048c968dc6'
NETWORK_ID = 'L_686798943174017585'

# Function to grant access to a specific client device in Meraki
def grant_access_in_meraki(client_mac_address):
    # Construct URL for Meraki API endpoint
    url = f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/clients/{client_mac_address}/policy"
    # Define policy details (modify as needed)
    policy = {
        "devicePolicy": "Group policy or SSID policy ID",
        "devicePolicyType": "Group policy or SSID policy type"
    }
    # Define headers for the API request
    headers = {
        'X-Cisco-Meraki-API-Key': MERAKI_API_KEY,
        'Content-Type': 'application/json'
    }
    # Send PUT request to Meraki API to update client policy
    response = requests.put(url, json=policy, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return True
    else:
        return False

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

    # Extract the client's MAC address from the Webex response (modify as per your Webex integration)
    client_mac_address = 'CLIENT_MAC_ADDRESS_FROM_WEBEX'

    # Grant access in Meraki using the extracted MAC address
    if grant_access_in_meraki(client_mac_address):
        return 'Logged in successfully! Access granted in Meraki.'
    else:
        return 'Logged in successfully, but access was not granted in Meraki.'

@webex.tokengetter
def get_webex_oauth_token():
    # Retrieve the stored Webex OAuth token from the session
    return session.get('webex_token')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
