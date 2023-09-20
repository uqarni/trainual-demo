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
    state = get_state(my_var=1, activated="yes")

    # Create a title for the chat interface
    st.title("Trainual Bot (named Tracy)")
    st.write("To test, first select some fields then click the button below.")
  
    #variables for system prompt
    name = 'Tracy'
    booking_link = 'trainualbooking.com'
    lead_first_name = st.text_input('Lead First Name', value = 'John')
    promo_code = st.text_input('promo code', value = 'Trainual50')
    
    # Capture the activated state from the selectbox and update the session state
    state.activated = st.selectbox('activated', ['yes', 'no'])

    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(lead_first_name = lead_first_name, promo_code = promo_code, activation_date = state.activated)

    initial_text = bot_info['initial_text']
    initial_text = initial_text.format(lead_first_name = lead_first_name)
    
    if st.button('Click to Start or Restart'):
        reset_variable(state)
        state.activated = 'yes'

    userresponse = st.text_input("Enter your message")
    
    if st.button("Send"):
        #prep the json
        newline = {"role": "user", "content": userresponse}

        #append to database
        with open('database.jsonl', 'a') as f:
            # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages)

        #append to database
        with open('database.jsonl', 'a') as f:
            for i in range(count):
                f.write(json.dumps(messages[-count + i]) + '\n')

        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            if 'This is a secret internal thought' not in str(message):
                string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)


    if st.button("Increment Day"):
        increment_variable(state)
        # Your increment logic remains unchanged...

    st.write(f"*Currently in Day:* {state.my_var}")

if __name__ == '__main__':
    main()
