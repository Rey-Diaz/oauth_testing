import requests

API_KEY = '91827e9abc34e868af813bb69ce997048c968dc6'  # Replace with your Meraki API key
BASE_URL = 'https://api.meraki.com/api/v1'

headers = {
    'X-Cisco-Meraki-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Get the list of organizations associated with the API key
orgs_response = requests.get(f'{BASE_URL}/organizations', headers=headers)
orgs_response.raise_for_status()
orgs = orgs_response.json()

for org in orgs:
    print(f"Organization Name: {org['name']}, Organization ID: {org['id']}")


if not orgs:
    print("No organizations found for the provided API key.")
    exit()

# Assuming you have only one organization, get its ID
org_id = orgs[0]['id']

# Get the list of networks associated with the organization
networks_response = requests.get(f'{BASE_URL}/organizations/{org_id}/networks', headers=headers)
networks_response.raise_for_status()
networks = networks_response.json()

if not networks:
    print(f"No networks found for organization ID: {org_id}.")
    exit()

# Print the network IDs
for network in networks:
    print(f"Network Name: {network['name']}, Network ID: {network['id']}")

