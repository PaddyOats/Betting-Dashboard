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
        
        # Prepare dictionary to store odds for each bookmaker
        bookmaker_odds = {
            'Bookmaker': [],
            'Home Team Odds': [],
            'Away Team Odds': [],
            'Draw Odds': [],
            'Home Fractional Odds': [],
            'Away Fractional Odds': [],
            'Draw Fractional Odds': []
        }
        
        # Iterate through bookmakers
        for bookmaker in match['bookmakers']:
            bookmaker_name = bookmaker['title']
            
            # Check if the bookmaker is in the allowed list
            if bookmaker_name in allowed_bookmakers:
                # Iterate through markets and outcomes
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':  # Head-to-head market
                        home_odds = None
                        away_odds = None
                        draw_odds = None
                        home_fractions = None
                        away_fractions = None
                        draw_fractions = None
                        
                        # Find odds for each outcome
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                home_odds = outcome['price']
                                home_fractions = decimal_to_fraction(home_odds)
                            elif outcome['name'] == away_team:
                                away_odds = outcome['price']
                                away_fractions = decimal_to_fraction(away_odds)
                            elif outcome['name'] == "Draw":
                                draw_odds = outcome['price']
                                draw_fractions = decimal_to_fraction(draw_odds)

                        # Add the bookmaker odds and fractional odds to the table
                        bookmaker_odds['Bookmaker'].append(bookmaker_name)
                        bookmaker_odds['Home Team Odds'].append(home_odds)
                        bookmaker_odds['Away Team Odds'].append(away_odds)
                        bookmaker_odds['Draw Odds'].append(draw_odds)
                        bookmaker_odds['Home Fractional Odds'].append(home_fractions)
                        bookmaker_odds['Away Fractional Odds'].append(away_fractions)
                        bookmaker_odds['Draw Fractional Odds'].append(draw_fractions)

        # Predict outcome based on odds (simple comparison)
        home_odds_best = min(bookmaker_odds['Home Team Odds'])
        away_odds_best = min(bookmaker_odds['Away Team Odds'])

        if home_odds_best < away_odds_best:
            predicted_outcome = f"Home Win ({home_team})"
        elif home_odds_best > away_odds_best:
            predicted_outcome = f"Away Win ({away_team})"
        else:
            predicted_outcome = "Draw"
        
        # Add the predicted outcome to the table
        bookmaker_odds['Bookmaker'].append("Prediction")
        bookmaker_odds['Home Team Odds'].append("")
        bookmaker_odds['Away Team Odds'].append("")
        bookmaker_odds['Draw Odds'].append("")
        bookmaker_odds['Home Fractional Odds'].append("")
        bookmaker_odds['Away Fractional Odds'].append("")
        bookmaker_odds['Draw Fractional Odds'].append(predicted_outcome)

    # Create a dataframe from the table data
    df = pd.DataFrame(bookmaker_odds)

    # Display the table
    st.dataframe(df)

else:
    st.error("Failed to fetch data or no data available.")
