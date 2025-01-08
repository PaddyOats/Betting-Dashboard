import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# API endpoint and key
url = "https://api.the-odds-api.com/v4/sports/soccer_spl/odds"
api_key = "2ae55a4b733022aba15d177da16e7251"  # Your API Key

# Function to convert decimal odds to fractional odds
def decimal_to_fraction(decimal_odds):
    numerator = decimal_odds - 1
    denominator = 1
    while (numerator % 1 != 0):
        numerator *= 10
        denominator *= 10
    gcd = find_gcd(int(numerator), int(denominator))
    return f"{int(numerator / gcd)}/{int(denominator / gcd)}"

# Function to find GCD for simplification
def find_gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Filtered bookmakers in Ireland and the UK
allowed_bookmakers = ['Marathon Bet', '888sport', 'Coolbet', 'Bet365', 'William Hill', 'Paddy Power']

# Fetch odds data
params = {
    'apiKey': api_key,
    'regions': 'eu',  # Filter for European region (Ireland, UK)
    'markets': 'h2h',  # Head-to-head odds
    'oddsFormat': 'decimal',  # Decimal odds format
}

response = requests.get(url, params=params)
data = response.json()

# Check if the data exists and if it's in the expected format
if response.status_code == 200 and data:
    st.title("Sports Betting Dashboard")
    
    # Prepare a list to store data for the table
    table_data = []

    # Iterate through matches
    for match in data:
        match_id = match['id']
        home_team = match['home_team']
        away_team = match['away_team']
        league = match['sport_title']
        match_date = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        
        # Iterate through bookmakers
        for bookmaker in match['bookmakers']:
            bookmaker_name = bookmaker['title']
            
            # Check if the bookmaker is in the allowed list
            if bookmaker_name in allowed_bookmakers:
                # Iterate through markets and outcomes
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':  # Head-to-head market
                        for outcome in market['outcomes']:
                            team_name = outcome['name']
                            decimal_odds = outcome['price']
                            fractional_odds = decimal_to_fraction(decimal_odds)

                            # Append data for the table (one row per match)
                            table_data.append([league, match_date, home_team, away_team, bookmaker_name, team_name, decimal_odds, fractional_odds])

    # Create a dataframe from the table data
    df = pd.DataFrame(table_data, columns=["League", "Date", "Home Team", "Away Team", "Bookmaker", "Team", "Decimal Odds", "Fractional Odds"])

    # Display the table
    st.dataframe(df)

else:
    st.error("Failed to fetch data or no data available.")
