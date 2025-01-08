import requests
import streamlit as st

# API endpoint and key
url = "https://api.the-odds-api.com/v4/sports/soccer_spl/odds"
api_key = "2ae55a4b733022aba15d177da16e7251"  # Your API Key

# Fetch odds data
params = {
    'apiKey': api_key,
    'regions': 'us',  # Filter for specific region (if needed)
    'markets': 'h2h',  # Head-to-head odds
    'oddsFormat': 'decimal',  # Decimal odds format
}

response = requests.get(url, params=params)
data = response.json()

# Check if the data exists and if it's in the expected format
if response.status_code == 200 and data:
    st.title("Sports Betting Dashboard")
    
    for match in data:
        st.subheader(f"{match['home_team']} vs {match['away_team']}")

        # Iterate through bookmakers and display odds
        for bookmaker in match['bookmakers']:
            st.write(f"Bookmaker: {bookmaker['title']}")

            # Iterate through markets and display outcomes
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':  # Head-to-head market
                    for outcome in market['outcomes']:
                        st.write(f"  Team: {outcome['name']} | Odds: {outcome['price']}")

else:
    st.error("Failed to fetch data or no data available.")
