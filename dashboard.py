import requests
import pandas as pd
import streamlit as st

# Your API key here
api_key = "2ae55a4b733022aba15d177da16e7251"

# URL and params for the API request
url = "https://api.the-odds-api.com/v4/sports/odds"
params = {
    'apiKey': api_key,
    'regions': 'eu',  # Filter for European region (Ireland, UK)
    'markets': 'h2h',  # Head-to-head odds
    'oddsFormat': 'decimal',  # Decimal odds format
    'leagues': 'soccer_epl,soccer_seriea,soccer_laliga,soccer_bundesliga,soccer_spl'  # Add more leagues
}

# Fetch the data
response = requests.get(url, params=params)

# Check if the response is valid before trying to parse JSON
if response.status_code == 200:
    # If the request is successful, parse the JSON response
    data = response.json()

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Clean and transform the DataFrame
    def odds_to_fraction(odds_decimal):
        # Convert decimal odds to fractional odds
        numerator = round(odds_decimal - 1)
        denominator = 1
        return f'{numerator}/{denominator}'

    # Prepare DataFrame
    for index, row in df.iterrows():
        fixture = row['home_team'] + " vs " + row['away_team']
        row['fixture'] = fixture
        for bookmaker in row['bookmakers']:
            bookmaker_title = bookmaker['title']
            for market in bookmaker['markets']:
                for outcome in market['outcomes']:
                    outcome_name = outcome['name']
                    outcome_price = odds_to_fraction(outcome['price'])
                    row[f"{bookmaker_title} - {outcome_name}"] = outcome_price

    # Display table with the fixtures and odds
    st.title("Betting Odds Dashboard")
    st.write(df[['fixture', 'bookmakers']])

    # Optionally, highlight best bets of the day based on some criteria (simplified here)
    st.subheader("Best Bet of the Day")
    best_bet = df.iloc[df['bookmakers'].apply(lambda x: min(x)).idxmin()]
    st.write(best_bet[['fixture', 'bookmakers']])

else:
    # If the request fails, print the error and status code
    st.write(f"Error fetching data. HTTP Status Code: {response.status_code}")
