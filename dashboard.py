import requests

api_key = "2ae55a4b733022aba15d177da16e7251"
url = "https://api.the-odds-api.com/v4/sports/odds"

# Simplified parameters to start with
params = {
    'apiKey': api_key,
    'regions': 'eu',  # Filter for European region (Ireland, UK)
    'markets': 'h2h',  # Head-to-head odds
    'oddsFormat': 'decimal',  # Decimal odds format
}

response = requests.get(url, params=params)

if response.status_code == 200:
    print(response.json())  # Output the response JSON to verify the data
else:
    print(f"Error fetching data. HTTP Status Code: {response.status_code}")
