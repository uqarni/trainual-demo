import streamlit as st
from functions import ideator, secret_message
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(urL, key)
data, count = supabase.table("bots_dev").select("*").eq("id", "allison").execute()
bot_info = data[1][0]

# id
# org_id
# system_prompt
# max_followup_count
# followup_time
# followup_prompt

class _SessionState:
    def __init__(self, activation_date="no", **kwargs):
        self.activation_date = activation_date
        for key, val in kwargs.items():
            setattr(self, key, val)


def get_state(**kwargs):
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = _SessionState(**kwargs)
    return st.session_state['session_state']


def increment_variable(state):
    state.my_var += 1

def reset_variable(state):
    state.my_var = 1

def main():
    day = get_state(my_var=1)
    # Create a title for the chat interface
    st.title("Trainual Bot (named Tracy)")
    st.write("To test, first select some fields then click the button below.")
  
    #variables for system prompt
    name = 'Tracy'
    booking_link = 'trainualbooking.com'
    
    lead_first_name = st.text_input('Lead First Name', value = 'John')
    promo_code = st.text_input('promo code', value = 'Trainual50')

    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(lead_first_name = lead_first_name, promo_code = promo_code, activation_date = day.activation_date)

    
    initial_text = bot_info['initial_text']
    initial_text = initial_text.format(lead_first_name = lead_first_name)
    
    if st.button('Click to Start or Restart'):
        reset_variable(day)
        day.activation_date = 'no'
        st.write(initial_text)
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl','a') as arch:
        # add reset 
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        #copy each line from db to archive
            for line in db:
                arch.write(line)

        #clear database to only first two lines
        with open('database.jsonl', 'w') as f:
        # Override database with initial json files
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": initial_text}            
            ]
            f.write(json.dumps(messages[0])+'\n')
            f.write(json.dumps(messages[1])+'\n')



    #initialize messages list and print opening bot message
    #st.write("Hi! This is Tara. Seems like you need help coming up with an idea! Let's do this. First, what's your job?")

    # Create a text input for the user to enter their message and append it to messages
    userresponse = st.text_input("Enter your message")
    

    # Create a button to submit the user's message
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
        print(string)
        
    if day.activation_date == 'no':
        if st.button("Toggle Activation"):
            if day.activation_date == "no":
                day.activation_date = "yes" 
            #extract messages out to list
            messages = []

            with open('database.jsonl', 'r') as f:
                for line in f:
                    json_obj = json.loads(line)
                    messages.append(json_obj)

            # Display the response in the chat interface
            string = ""

            for message in messages[1:]:
                if 'secret internal thought' not in str(message):
                    string = string + message["role"] + ": " + message["content"] + "\n\n"
            st.write(string)
            print(string)

    
    if st.button("Increment Day"):
        increment_variable(day)
        
        if int(day.my_var) <= 7:
            
            newline = secret_message(day.my_var, day.activation_date)
            with open('database.jsonl', 'a') as f:
                f.write(json.dumps(newline) + '\n')
        
            # Your existing code for reading the database, generating responses, and updating the database can remain here
            # extract messages out to list
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
                if "secret internal thought"  not in str(message):
                    string = string + message["role"] + ": " + message["content"] + "\n\n"
            st.write(string)
            print(string)
        else:
            st.write('Trial ended. Bot will not send messages. Please reset to start again.')

    # At the bottom of your Streamlit layout, you can show the current week
    st.write(f"*Currently in Day:* {day.my_var}")
    st.write(f"*is user activated?* {day.activation_date}")
        

if __name__ == '__main__':
    main()
