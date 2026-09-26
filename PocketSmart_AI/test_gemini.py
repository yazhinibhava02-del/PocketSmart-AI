from PIL import Image
from google import genai

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
try:
    print("Testing Gemini 3.5 Flash...")
    img = Image.open("outfit.jpg")

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            img,
            (
                "Suggest 2 budget-friendly jewelry matching this outfit under"
                " 2000 INR."
            ),
        ],
    )

    print("\n--- MULTIMODAL TEST SUCCESS ---")
    print(response.text)

except FileNotFoundError:
    print("outfit.jpg file folder-la illa! Simple text mattum test panrom...")
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Say 'PocketSmart AI Gemini 3.5 Flash is ready!'",
    )
    print("\n--- TEXT TEST SUCCESS ---")
    print(response.text)

except Exception as e:
    print(f"\nError: {e}")