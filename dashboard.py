import streamlit as st
import pandas as pd
import requests

# Title
st.title("Betting Dashboard")

# Input: Odds API Key
api_key = '2ae55a4b733022aba15d177da16e7251'  # Your actual API key

# Fetching sample data
st.subheader("Daily Bets")
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds?apiKey={api_key}&regions=eu"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # Display the raw response to understand its structure
    st.write(data)  # Print the raw API response to debug
else:
    st.write("Error fetching odds data!")

# Best Odds of the Day (Optional: This part is to identify the bet with the best odds)
st.subheader("Best Odds of the Day")
if response.status_code == 200 and data:
    try:
        # Check if bookmakers and odds exist in the response
        best_bet = max(data, key=lambda x: max([b['odds'] for b in x.get('bookmakers', [])])) 
        st.write(f"Best Odds: {best_bet['bookmakers'][0]['odds']}")
    except KeyError as e:
        st.write(f"Error processing best bet: {e}")
else:
    st.write("Error fetching or processing data.")
