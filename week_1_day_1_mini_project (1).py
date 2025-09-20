readme = """
# GPT Function Calling Assistant

This assistant uses OpenAI GPT-4o's function calling to:
- Return the current date/time
- Generate to-do lists based on a given topic

### Example Prompts:
- What time is it?
- Can you make me a to-do list to start a clothing brand?

### Files:
- main.py or .ipynb: Main logic
- requirements.txt: Dependencies
- README.md: This file

### Run Instructions:
```bash
pip install -r requirements.txt
python main.py
"""
with open("README.md", "w") as f:
  f.write(readme)
!cat README.md  # to preview

!pip install --quiet openai

from openai import OpenAI
import getpass
import datetime
import json

# Prompt for API key securely (don’t hardcode in shared notebooks)
api_key = getpass.getpass("Enter your OpenAI API key: ")
client = OpenAI(api_key=api_key)

"""
GPT Function Calling Assistant

This tool uses OpenAI's GPT-4o model to:
- Return the current date/time
- Generate to-do lists based on a topic
You can expand this with more functions like motivational quotes or reminders.
"""

# This function returns the current date and time as a dictionary
def get_current_datetime():
    now = datetime.datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    }

# This function generates a simple numbered to-do list for a given topic
def generate_todo_list(topic, num_items=5):
    return {
        "topic": topic,
        "items": [f"Task {i+1} for {topic}" for i in range(num_items)]
    }

# Define function schemas to tell GPT what tools are available and how they work
functions = [
    {
        "name": "get_current_datetime",
        "description": "Returns the current date and time.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "generate_todo_list",
        "description": "Generates a list of tasks for a given topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "num_items": {"type": "integer", "default": 5}
            },
            "required": ["topic"]
        }
    }
]

# user input that the GPT will interpret to decide whether to call a function
user_prompt = "Can I have a to-do list to learn about markets in the stock market?"

# Call the OpenAPI API and ask GPT to choose which function (if any) to call
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": user_prompt}],
    functions=functions,
    function_call="auto" # GPT decides whether and which function to use
)

# Extract the returned message (which may include a function call)
message = response.choices[0].message

# IF GPT chose to call a function, run that function with the arguments it provided
if message.function_call:
    function_name = message.function_call.name
    arguments = json.loads(message.function_call.arguments)

# If GPT requested the date/time run this function
    if function_name == "get_current_datetime":
        result = get_current_datetime()

# If GPT requested a to-do list, run that function with topic + optional comments if needed.
    elif function_name == "generate_todo_list":
        result = generate_todo_list(
            topic=arguments.get("topic"),
            num_items=arguments.get("num_items", 5)
        )

# Send GPT the actual result of the function so it can reply naturally to the user
    second_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": user_prompt}, # Original User Message
            message.model_dump(),    # GPT's original function call
            {
                "role": "function",
                "name": function_name,
                "content": json.dumps(result)   # The result from our function
            }
        ]
    )

    # Final result from GPT
    print("GPT's Final Reply:\n", second_response.choices[0].message.content)
