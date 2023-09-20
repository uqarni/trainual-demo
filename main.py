import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(urL, key)
data, count = supabase.table("bots").select("*").eq("id", "allison").execute()
bot_info = data[1][0]

class _SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get_state(**kwargs):
    if 'session_state' not in st.session_state:
        st.session_state.session_state = _SessionState(**kwargs)
    return st.session_state.session_state

def increment_variable(state):
    state.my_var += 1

def reset_variable(state):
    state.my_var = 1

def main():
    # Get session state variables
    day = get_state(my_var=1)
    state = get_state(activated="yes")

    # Create a title for the chat interface
    st.title("Trainual Bot (named Tracy)")
    st.write("To test, first select some fields then click the button below.")
  
    #variables for system prompt
    name = 'Tracy'
    booking_link = 'trainualbooking.com'
    
    lead_first_name = st.text_input('Lead First Name', value = 'John')
    promo_code = st.text_input('promo code', value = 'Trainual50')
    
    # Capture the activated state from the selectbox and update the session state
    activated = st.selectbox('activated', ['yes', 'no'])
    state.activated = activated

    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(lead_first_name = lead_first_name, promo_code = promo_code, activation_date = activated)

    initial_text = bot_info['initial_text']
    initial_text = initial_text.format(lead_first_name = lead_first_name)
    
    if st.button('Click to Start or Restart'):
        # ... [your existing code]
        reset_variable(day)
        state.activated = 'yes'  # Resetting to default for a fresh start

    userresponse = st.text_input("Enter your message")
    
    if st.button("Send"):
        # ... [your existing code]
        # Update activated state based on your logic if needed here

    if st.button("Increment Day"):
        # ... [your existing code]
        # Update activated state based on your logic if needed here

    # At the bottom of your Streamlit layout, you can show the current week
    st.write(f"*Currently in Day:* {day.my_var}")

if __name__ == '__main__':
    main()
