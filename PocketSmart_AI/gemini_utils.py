import json
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables from .env
load_dotenv()
import os
from dotenv import load_dotenv

load_dotenv()

# Secure line - pulls from .env file directly
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Models to attempt with fallback mechanism
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def _clean_json_response(text: str) -> dict:
    """Helper function to cleanly parse JSON from LLM markdown fences."""
    try:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        clean_text = match.group(1).strip() if match else text.strip()
        return json.loads(clean_text)
    except Exception:
        return {}


def _generate_with_fallback(prompt: str, image: Image.Image = None) -> str:
    """Tries primary model and falls back if rate limits or 503 occur."""
    contents = [prompt]
    if image:
        contents.append(image)

    last_error = None
    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            if response.text:
                return response.text
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"All Gemini models failed. Error: {last_error}")


# 1. Home Interior Planner Logic
def get_home_recommendations(budget: float, room_type: str, items: dict) -> dict:
    prompt = f"""
    You are an expert home interior budget planner for the Indian market.
    Budget: Rs. {budget}
    Room Type: {room_type}
    Requested Items & Quantities: {json.dumps(items)}

    Recommend cost-effective, real-world style items available on platforms like IKEA, Amazon, and Flipkart.
    Ensure total spent is strictly less than or equal to Rs. {budget}.
    
    Output strictly valid JSON with this exact structure:
    {{
        "total_allocated": 12000,
        "remaining_reserve": 3000,
        "summary": "Short explanation of the budget split.",
        "items": [
            {{
                "name": "Product Name",
                "platform": "IKEA / Amazon / Flipkart",
                "price": 4500,
                "reason": "Why this item fits the room and budget."
            }}
        ]
    }}
    """
    try:
        raw_output = _generate_with_fallback(prompt)
        parsed = _clean_json_response(raw_output)
        if parsed and "items" in parsed:
            return parsed
    except Exception as e:
        print(f"Home planner AI error: {e}")

    # Graceful fallback data if AI fails
    return {
        "total_allocated": budget * 0.85,
        "remaining_reserve": budget * 0.15,
        "summary": f"Standard curated setup for {room_type} within ₹{budget}.",
        "items": [
            {
                "name": "Minimalist Center Table",
                "platform": "Flipkart",
                "price": budget * 0.40,
                "reason": "Durable and affordable everyday anchor piece.",
            },
            {
                "name": "Warm Ambient Floor Lamp",
                "platform": "Amazon",
                "price": budget * 0.25,
                "reason": "Cost-effective ambient lighting.",
            },
            {
                "name": "Wall Mount Wooden Shelves",
                "platform": "IKEA",
                "price": budget * 0.20,
                "reason": "Vertical storage saving floor area.",
            },
        ],
    }


# 2. Party Planner Logic
def get_party_recommendations(
    budget: float, event_type: str, guest_count: int, venue_details: str
) -> dict:
    prompt = f"""
    You are an expert party budget planner in India.
    Event Type: {event_type}
    Total Budget: Rs. {budget}
    Number of Guests: {guest_count}
    Venue: {venue_details}

    Allocate the budget realistically across Catering (Swiggy / Zomato / local vendors), 
    Decorations (Amazon / local vendors), and Essentials/Venue.
    Total allocated cost must not exceed Rs. {budget}.

    Output strictly valid JSON with this exact structure:
    {{
        "total_allocated": 14000,
        "per_guest_cost": 700,
        "summary": "Brief summary of the party plan distribution.",
        "categories": [
            {{
                "category": "Catering",
                "vendor_platform": "Zomato / Swiggy / Local Caterers",
                "allocated_amount": 8000,
                "description": "Party snack boxes & beverages"
            }},
            {{
                "category": "Decorations",
                "vendor_platform": "Amazon",
                "allocated_amount": 3500,
                "description": "Fairy lights, balloons, banners"
            }},
            {{
                "category": "Entertainment & Cake",
                "vendor_platform": "Local Bakery / Amazon",
                "allocated_amount": 2500,
                "description": "Custom celebration cake and audio rental"
            }}
        ]
    }}
    """
    try:
        raw_output = _generate_with_fallback(prompt)
        parsed = _clean_json_response(raw_output)
        if parsed and "categories" in parsed:
            return parsed
    except Exception as e:
        print(f"Party planner AI error: {e}")

    # Fallback party budget calculation
    catering_amt = budget * 0.55
    decor_amt = budget * 0.25
    other_amt = budget * 0.20
    return {
        "total_allocated": budget,
        "per_guest_cost": round(budget / max(guest_count, 1), 2),
        "summary": f"Balanced event allocation for {guest_count} guests at {venue_details}.",
        "categories": [
            {
                "category": "Catering & Refreshments",
                "vendor_platform": "Zomato / Swiggy Bulk Order",
                "allocated_amount": catering_amt,
                "description": "Full meals or appetizers package suited for group count.",
            },
            {
                "category": "Theme Decor & Lighting",
                "vendor_platform": "Amazon",
                "allocated_amount": decor_amt,
                "description": "Fairy lights, party banner, paper pom-poms, photo backdrop.",
            },
            {
                "category": "Cake & Logistics Reserve",
                "vendor_platform": "Local Vendor",
                "allocated_amount": other_amt,
                "description": "Celebration cake, disposable cutlery, and emergency buffer.",
            },
        ],
    }


# 3. Multimodal Jewelry Matcher Logic
def get_jewelry_recommendations(
    budget: float, occasion: str, style_pref: str, image_path: str = None
) -> dict:
    image_obj = None
    if image_path and os.path.exists(image_path):
        try:
            image_obj = Image.open(image_path)
        except Exception as img_err:
            print(f"Image load warning: {img_err}")

    prompt = f"""
    You are a professional fashion stylist and jewelry advisor in India.
    Target Budget: Rs. {budget}
    Occasion: {occasion}
    Style Preference: {style_pref}

    Analyze the user's requirements (and the provided outfit photo if attached).
    Suggest matching jewelry pieces from platforms like GIVA, Voylla, Amazon, or CaratLane within the total budget of Rs. {budget}.

    Output strictly valid JSON with this exact structure:
    {{
        "style_analysis": "2-3 sentences explaining why this jewelry matches the outfit/occasion.",
        "total_allocated": 2800,
        "recommendations": [
            {{
                "name": "Product Name",
                "brand": "GIVA / Voylla / Amazon",
                "price": 1800,
                "match_reason": "Specific aesthetic matching explanation."
            }}
        ]
    }}
    """
    try:
        raw_output = _generate_with_fallback(prompt, image=image_obj)
        parsed = _clean_json_response(raw_output)
        if parsed and "recommendations" in parsed:
            return parsed
    except Exception as e:
        print(f"Jewelry matcher AI error: {e}")

    # Fallback styling recommendation
    return {
        "style_analysis": f"For a {occasion} look with {style_pref} preference, minimal contemporary metallic accents provide an elegant sparkle without overpowering your attire.",
        "total_allocated": budget * 0.90,
        "recommendations": [
            {
                "name": "Sterling Silver / Rose Gold Zircon Pendant",
                "brand": "GIVA",
                "price": budget * 0.60,
                "match_reason": "Clean contemporary silhouette suited for evening lights.",
            },
            {
                "name": "Classic Geometric Drop Earrings",
                "brand": "Voylla",
                "price": budget * 0.30,
                "match_reason": "Subtle flair that perfectly complements the neckline.",
            },
        ],
    }