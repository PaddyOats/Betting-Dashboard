import streamlit as st
import pandas as pd
import requests

# Title
st.title("Betting Dashboard")

# Input: Odds API Key
api_key = "2ae55a4b733022aba15d177da16e7251"

# Fetching sample data
st.subheader("Daily Bets")
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds?apiKey={api_key}&regions=eu"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    bets_df = pd.json_normalize(data)
    st.write(bets_df)
else:
    st.write("Error fetching odds data!")
