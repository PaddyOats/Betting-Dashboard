import requests
import pandas as pd
import streamlit as st
from fractions import Fraction

# Function to convert decimal odds to fractional odds
def decimal_to_fraction(decimal_odds):
    if decimal_odds > 1:
        frac = Fraction(decimal_odds - 1).limit_denominator()
        return f"{frac.numerator}/{frac.denominator}"
    else:
        return "N/A"

# Function to fetch data from the Odds API
def fetch_odds_data():
    api_key = "2ae55a4b733022aba15d177da16e7251"  # Your API key
    url = "https://api.the-odds-api.com/v4/sports/odds"

    params = {
        'apiKey': api_key,
        'regions': 'eu',  # Europe
        'markets': 'h2h',  # Head-to-head odds
        'oddsFormat': 'decimal',  # Decimal odds format
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # Return the data if the request is successful
    else:
        st.error(f"Error fetching data. HTTP Status Code: {response.status_code}")
        return []

# Function to get the best bet of the day
def get_best_bet(row):
    # Find the bookmaker with the highest odds for the home team
    home_odds = [row[bookmaker]['Home Team Odds'] for bookmaker in row if isinstance(row[bookmaker], dict)]
    if home_odds:
        best_home_odds = max(home_odds)
        return decimal_to_fraction(best_home_odds)  # Convert decimal odds to fractional
    return "N/A"

# Fetch odds data from the API
data = fetch_odds_data()

if data:
    # Initialize lists for storing the data
    match_data = []
    for match in data:
        home_team = match['home_team']
        away_team = match['away_team']
        league = match['sport_title']
        match_date = match['commence_time']

        # Bookmaker odds
        bookmaker_odds = {}
        for bookmaker in match['bookmakers']:
            bookmaker_name = bookmaker['title']
            odds_data = bookmaker['markets'][0]['outcomes']
            home_odds = next((item['price'] for item in odds_data if item['name'] == home_team), None)
            away_odds = next((item['price'] for item in odds_data if item['name'] == away_team), None)
            draw_odds = next((item['price'] for item in odds_data if item['name'] == 'Draw'), None)

            bookmaker_odds[bookmaker_name] = {
                'Home Team Odds': home_odds,
                'Away Team Odds': away_odds,
                'Draw Odds': draw_odds
            }

        # Add match info and odds to match_data
        match_data.append({
            'Match': f"{home_team} vs {away_team}",
            'League': league,
            'Date': match_date,
            **bookmaker_odds
        })

    # Create a DataFrame from the match_data
    df = pd.DataFrame(match_data)

    # Convert decimal odds to fractional odds for each bookmaker
    for bookmaker in df.columns:
        if bookmaker not in ['Match', 'League', 'Date']:
            df[bookmaker] = df[bookmaker].apply(lambda x: decimal_to_fraction(x) if isinstance(x, (int, float)) else "N/A")

    # Add a new column for the best bet
    df['Best Bet'] = df.apply(get_best_bet, axis=1)

    # Display the data in a table format
    st.write("### Football Odds Overview")
    st.dataframe(df)

    # Display best bet of the day
    best_bet = df['Best Bet'].max()  # Get the best bet of the day (highest fractional odds)
    st.write(f"### Best Bet of the Day: {best_bet}")

else:
    st.write("No data available.")

