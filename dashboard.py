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

# Display the raw response for inspection
st.write("API Response Status:", response.status_code)
if response.status_code == 200:
    data = response.json()
    
    # Displaying the entire API response for debugging
    st.write("Raw API Response:", data)  # This should print the whole response

    if isinstance(data, list) and len(data) > 0:
        first_item = data[0]
        st.write("First item in the response:", first_item)  # Show the first item in the list

        # Display the fields of the first item
        st.write("Fields in the first item:", first_item.keys())

        # Check if 'bookmakers' exists and display it
        bookmakers = first_item.get('bookmakers', [])
        if bookmakers:
            st.write("Bookmakers data found:", bookmakers)

            for bookmaker in bookmakers:
                bookmaker_name = bookmaker.get('title', 'No title')
                bookmaker_odds = bookmaker.get('odds', 'No odds available')
                st.write(f"Bookmaker: {bookmaker_name} | Odds: {bookmaker_odds}")
        else:
            st.write("No bookmakers data found in the first item.")
    else:
        st.write("Data is empty or malformed.")
else:
    st.write("Error fetching odds data!")
