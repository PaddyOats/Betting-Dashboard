import streamlit as st
import pandas as pd
import requests

# Title
st.title("Betting Dashboard")

# Input: Odds API Key
api_key = "2ae55a4b733022aba15d177da16e7251"  # Replace this with your API key

# Subheader for Daily Bets Section
st.subheader("Daily Bets")

# Fetch Odds Data from API (this is just a placeholder URL)
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds?apiKey={api_key}&regions=eu"
response = requests.get(url)

# Check if the request was successful and parse the data
if response.status_code == 200:
    data = response.json()
    if data:
        # Normalize and display odds data
        bets_df = pd.json_normalize(data)
        st.write(bets_df.head())  # Display the first few rows to debug
    else:
        st.write("No data available!")
else:
    st.write("Error fetching odds data!")
    st.write(f"Error code: {response.status_code}")

# Sidebar for Filters (optional)
st.sidebar.header("Filters")
bookmakers = st.sidebar.selectbox("Choose a Bookmaker", ["Bet365", "William Hill", "Paddy Power"])
regions = st.sidebar.selectbox("Choose a Region", ["eu", "us", "uk"])

# Filter and display data based on the selected values
st.subheader(f"Bets from {bookmakers} in {regions} Region")

# Example: Displaying the highest odds of the day
st.subheader("Best Odds of the Day")
if response.status_code == 200 and data:
    # Assume each 'data' item contains a 'bookmakers' field with odds data
    best_bet = max(data, key=lambda x: max([b['odds'] for b in x['bookmakers']]))  # Example: Find the bet with the highest odds
    st.write(f"Best Odds: {best_bet['bookmakers'][0]['odds']}")  # Display the best odds (customize as per actual data)

