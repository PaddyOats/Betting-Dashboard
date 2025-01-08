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
    st.write("Raw API Data:", data)  # Display raw response for inspection

    # Check if bookmakers exist in the data
    if isinstance(data, list) and len(data) > 0:
        first_item = data[0]
        st.write("First item in data:", first_item)  # Show first data item
        bookmakers = first_item.get('bookmakers', [])
        
        # Check if bookmakers exist
        if bookmakers:
            st.write("Bookmakers data:", bookmakers)
            for bookmaker in bookmakers:
                st.write(f"Bookmaker: {bookmaker.get('title', 'Unknown')} Odds: {bookmaker.get('odds', 'No odds available')}")
        else:
            st.write("No bookmakers data found.")
    else:
        st.write("Data is empty or malformed.")
else:
    st.write("Error fetching odds data!")
