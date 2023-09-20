import openai
import os
import re
import random
from datetime import datetime, timedelta
import random

#generate random date
def random_date():
  start_date = datetime(2022, 1, 1)
  end_date = datetime.now()
  random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
  
  formatted_date = random_date.strftime("%Y-%m-%d")
  return formatted_date  # Outputs the random date in "YYYY-MM-DD" format



#generate openai response; returns messages with openai response
def ideator(messages):

  key = os.environ.get("OPENAI_API_KEY")
  openai.api_key = key

  result = openai.ChatCompletion.create(
    model="gpt-4",
    messages= messages
  )
  response = result["choices"][0]["message"]["content"]
  
  def split_sms(message):
      import re
  
      # Use regular expressions to split the string at ., !, or ? followed by a space or newline
      sentences = re.split('(?<=[.!?]) (?=\\S)|(?<=[.!?])\n', message.strip())
      # Strip leading and trailing whitespace from each sentence
      sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
  
      # Compute the cumulative length of all sentences
      cum_length = [0]
      for sentence in sentences:
          cum_length.append(cum_length[-1] + len(sentence))
      
      total_length = cum_length[-1]
  
      # Find the splitting point
      split_point = next(i for i, cum_len in enumerate(cum_length) if cum_len >= total_length / 2)
  
      # Split the sentences into two parts at the splitting point
      part1 = sentences[:split_point]
      part2 = sentences[split_point:]
  
      # Join the sentences in each part back into strings and exclude any part that is empty
      strings = []
      if part1:
          strings.append(" ".join(part1))
      if part2:
          strings.append(" ".join(part2))
      
      return strings

  split_response = split_sms(response)
  count = len(split_response)
  for section in split_response:
    section = {
      "role": "assistant", 
      "content": section
    }
    messages.append(section)

  return messages, count



def secret_message(day:int, activated: str):

    prepend = '[secret internal thought, not visible to the user] '
    seven = f"It's now the start of day {day}. Today is the last day of the trial, and I can proceed to Step 4. This means I need to ask if the user is ready to sign up for using Trainual. I have a promo code that will give them a special discount if they do."
    five_or_six = f"It's now the start of day {day}. I need to follow up for this day. If they've been an engaging lead so far, I must mention that the trial is going to wrap up soon, ask if there any remaining goals you want to accomplish; I'm here to help! If they have not been an engaging lead and explored some features in detail, I must remind them that the trial is coming to an end soon and I would love to show them how Trainual can help them. I'll also ask what was the main objective they were hoping to accomplish with this trial? "
    other = f"It's now the start of day {day}. I need to follow up for this day."
    active = " Also, I see this user is activated! Meaning they have either created content or invited a team member to Trainual. This means they are an active use and more likely to buy! I should push for the close!"
    inactive = " Also, I see this user is not activated. This means they have not created content or invited a team member to Trainual."
    
    if day == 7:
        to_send = prepend + seven
    elif day == 5 or day == 6:
        to_send = prepend + five_or_six
    else:
        to_send = prepend + other
    if activated == 'yes':
        to_send += active
    elif activated == 'no':
        to_send += inactive

    return {"role": "assistant", "content": to_send}