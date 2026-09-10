from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)