from openai import OpenAI
from Helpers.config import OPENAI_API_KEY

# Create an OpenAI client using the API key from the environment
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to send a prompt to OpenAI and get a response
def ask_openai(prompt: str, model="gpt-3.5-turbo", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in Amazon products."}, # System message sets the assistant's behavior
            {"role": "user", "content": prompt} # User message contains the prompt to be processed
        ],
        temperature=temperature
    )
    return response.choices[0].message.content
