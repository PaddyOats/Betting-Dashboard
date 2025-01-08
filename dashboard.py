import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# API endpoint and key
url = "https://api.the-odds-api.com/v4/sports/soccer_spl/odds"
api_key = "2ae55a4b733022aba15d177da16e7251"  # Your API Key

# Function to convert decimal odds to fractional odds
def decimal_to_fraction(decimal_odds):
    # Convert decimal to fraction and simplify
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
        home_team = match['home_team']
        away_team = match['away_team']
        league = match['sport_title']
        match_date = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare dictionary to store odds for each bookmaker
        bookmaker_odds = {
            'Fixture': f"{home_team} vs {away_team}",
            'League': league,
            'Date': match_date,
            'Home Team': home_team,
            'Away Team': away_team,
            'Best Bet': '',
        }
        
        # Initialize bookmaker columns
        for bookmaker in allowed_bookmakers:
            bookmaker_odds[bookmaker] = {}

        # Add the odds from each bookmaker
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

                        # Store the fractional odds for each bookmaker
                        bookmaker_odds[bookmaker_name] = {
                            'Home Team Odds': home_fractions,
                            'Away Team Odds': away_fractions,
                            'Draw Odds': draw_fractions
                        }

        # Add bookmaker odds data to table
        table_data.append(bookmaker_odds)

    # Create a dataframe from the table data
    df = pd.DataFrame(table_data)

    # Highlight best bet for each fixture based on lowest odds
    def get_best_bet(row):
        # Extract the odds for home, away, and draw
        home_odds = [row[bookmaker]['Home Team Odds'] for bookmaker in allowed_bookmakers if isinstance(row[bookmaker], dict)]
        away_odds = [row[bookmaker]['Away Team Odds'] for bookmaker in allowed_bookmakers if isinstance(row[bookmaker], dict)]
        draw_odds = [row[bookmaker]['Draw Odds'] for bookmaker in allowed_bookmakers if isinstance(row[bookmaker], dict)]

        # Find the best bet based on the lowest odds
        min_home = min(home_odds) if home_odds else None
        min_away = min(away_odds) if away_odds else None
        min_draw = min(draw_odds) if draw_odds else None

        if min_home and min_home <= min_away and min_home <= min_draw:
            return f"Best Bet: Home Win ({row['Home Team']})"
        elif min_away and min_away <= min_home and min_away <= min_draw:
            return f"Best Bet: Away Win ({row['Away Team']})"
        elif min_draw and min_draw <= min_home and min_draw <= min_away:
            return "Best Bet: Draw"
        return "No clear best bet"

    # Apply the best bet function to the dataframe
    df['Best Bet'] = df.apply(get_best_bet, axis=1)

    # Display the table
    st.dataframe(df)

else:
    st.error("Failed to fetch data or no data available.")
