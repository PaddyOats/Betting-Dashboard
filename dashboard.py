import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# API endpoint and key
url = "https://api.the-odds-api.com/v4/sports/odds"
api_key = "2ae55a4b733022aba15d177da16e7251"  # Your API Key

# Function to convert decimal odds to fractional odds
def decimal_to_fraction(decimal_odds):
    if decimal_odds is None:
        return None
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
    'leagues': 'soccer_epl,soccer_seriea,soccer_laliga,soccer_bundesliga,soccer_spl'  # Add more leagues
}

response = requests.get(url, params=params)

# Debugging: Print the raw response text to check for issues
st.write("Raw Response:", response.text)

# Check if the response is empty or failed
if response.status_code == 200:
    try:
        data = response.json()
        if not data:  # No data case
            st.error("No data available for the requested odds.")
        else:
            st.title("Sports Betting Dashboard")
            
            # Prepare a list to store data for the table
            table_data = []

            # Initialize variable to store best bet of the day
            best_bet_of_day = None
            best_bet_odds = None
            
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
                    bookmaker_odds[bookmaker] = {
                        'Home Team Odds': None,
                        'Away Team Odds': None,
                        'Draw Odds': None
                    }

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
                                
                                # Find odds for each outcome
                                for outcome in market['outcomes']:
                                    if outcome['name'] == home_team:
                                        home_odds = outcome['price']
                                    elif outcome['name'] == away_team:
                                        away_odds = outcome['price']
                                    elif outcome['name'] == "Draw":
                                        draw_odds = outcome['price']

                                # Convert decimal odds to fractional odds
                                bookmaker_odds[bookmaker_name] = {
                                    'Home Team Odds': decimal_to_fraction(home_odds),
                                    'Away Team Odds': decimal_to_fraction(away_odds),
                                    'Draw Odds': decimal_to_fraction(draw_odds)
                                }

                # Add bookmaker odds data to table
                table_data.append(bookmaker_odds)

                # Calculate best bet of the day
                home_odds_list = [bookmaker_odds[bookmaker]['Home Team Odds'] for bookmaker in allowed_bookmakers if bookmaker_odds[bookmaker]['Home Team Odds']]
                away_odds_list = [bookmaker_odds[bookmaker]['Away Team Odds'] for bookmaker in allowed_bookmakers if bookmaker_odds[bookmaker]['Away Team Odds']]
                draw_odds_list = [bookmaker_odds[bookmaker]['Draw Odds'] for bookmaker in allowed_bookmakers if bookmaker_odds[bookmaker]['Draw Odds']]
                
                min_home_odds = min(home_odds_list) if home_odds_list else None
                min_away_odds = min(away_odds_list) if away_odds_list else None
                min_draw_odds = min(draw_odds_list) if draw_odds_list else None
                
                # Find the best bet for the day (i.e., highest odds for a home win, away win, or draw)
                if min_home_odds and (best_bet_odds is None or min_home_odds > best_bet_odds):
                    best_bet_of_day = f"{home_team} to win"
                    best_bet_odds = min_home_odds
                elif min_away_odds and (best_bet_odds is None or min_away_odds > best_bet_odds):
                    best_bet_of_day = f"{away_team} to win"
                    best_bet_odds = min_away_odds
                elif min_draw_odds and (best_bet_odds is None or min_draw_odds > best_bet_odds):
                    best_bet_of_day = "Draw"
                    best_bet_odds = min_draw_odds

            # Create a dataframe from the table data
            df = pd.DataFrame(table_data)

            # Highlight best bet for each fixture based on lowest odds
            def get_best_bet(row):
                # Extract the odds for home, away, and draw
                home_odds = [row[bookmaker]['Home Team Odds'] for bookmaker in allowed_bookmakers if row[bookmaker]['Home Team Odds']]
                away_odds = [row[bookmaker]['Away Team Odds'] for bookmaker in allowed_bookmakers if row[bookmaker]['Away Team Odds']]
                draw_odds = [row[bookmaker]['Draw Odds'] for bookmaker in allowed_bookmakers if row[bookmaker]['Draw Odds']]

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

            # Add a section for Bet of the Day
            st.subheader("Bet of the Day")
            st.write(f"**Best Bet of the Day:** {best_bet_of_day} with odds {best_bet_odds}")
        else:
            st.error("No data found for the requested leagues.")
    except Exception as e:
        st.error(f"Error processing the data: {str(e)}")
else:
    st.error(f"Error fetching data. HTTP Status Code: {response.status_code}")
