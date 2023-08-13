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

# id
# org_id
# system_prompt
# max_followup_count
# followup_time
# followup_prompt


def main():

    # Create a title for the chat interface
    st.title("Trainual Bot (named Allison)")
    st.write("To test, first select some fields then click the button below.")
  
    #variables for system prompt
    name = 'Allison'
    booking_link = 'trainualbooking.com'

    filtration_field1 = st.write("***Filtered for [filtration data field 1]***")
    filtration_field2 = st.write("***Filtered for [filtration data field 2]***")
    
    lead_first_name = st.text_input('Lead First Name (leave blank for John)', value = 'John')
    custom_field1 = st.text_input('customization data field 2 (leave blank for unknown)', value = 'unknown')
    custom_field2 = st.text_input('customization data field 3 (leave blank for unknown)', value = 'unknown')

    system_prompt = bot_infp['system_prompt']
    system_prompt = system_prompt.format(first_name = lead_first_name, custom_field1 = custom_field1, custom_field2 = custom_field2)

    
    initial_text = st.text_input("Initial Text. Current value is 'Hi this is Allison from Trainual. Is this {first_name}'", value = 'Hi this is Allison from Trainual. Is this {first_name}?')
    initial_text = initial_text.format(first_name = lead_first_name)
    
    if st.button('Click to Start or Restart'):
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
            string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)
            

if __name__ == '__main__':
    main()
