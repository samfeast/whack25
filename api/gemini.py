import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("OTIS") 
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

def get_cheat_analysis_schema():
    """
    Defines the structured output schema for the Cheat game analysis.
    This ensures the model returns a predictable JSON object.
    """
    return {
        "type": "OBJECT",
        "properties": {
            "Bluffing": {
                "type": "BOOLEAN",
                "description": "True if the player is likely bluffing, False otherwise."
            },
            "Reasoning": {
                "type": "STRING",
                "description": "A 3-sentence summary of why this decision was made, analyzing the game state and emotion data."
            }
        },
        "propertyOrdering": ["Bluffing", "Reasoning"],
        "required": ["Bluffing", "Reasoning"]
    }

def generate_content(prompt, api_key, system_prompt=None, response_schema=None):
    """
    Sends a prompt to the Gemini API and returns the generated text.
    Includes support for guaranteed structured JSON output.

    Args:
        prompt (str): The text prompt to send to the model.
        api_key (str): Your API key for authentication.
        system_prompt (str, optional): Instructions to guide the model's behavior.
        response_schema (dict, optional): A dictionary defining the desired JSON structure.

    Returns:
        str: The generated text response (JSON string), or an error message.
    """
    if not api_key:
        return "Error: API Key is missing. Ensure 'OTIS' is set in your .env file."

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
    }
    
    if system_prompt:
        payload["systemInstruction"] = {
            "parts": [{"text": system_prompt}]
        }

    if response_schema:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }

    full_url = f"{API_URL}?key={api_key}"

    print(f"\n--- Sending Query: '{prompt[:40]}...' (Requesting JSON) ---")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(full_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            response_data = response.json()
            
            text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            
            if text:
                return text
            else:
                return f"API returned no text content. Response data:\n{json.dumps(response_data, indent=2)}"

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and response.status_code in [429, 500, 503]:
                wait_time = 2 ** attempt
                print(f"Request failed ({response.status_code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return f"Request failed: {e}. Final status code: {response.status_code if 'response' in locals() else 'N/A'}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    return "Failed to get response after multiple retries."


move = "Player 1 has played 2 4"
state = "1 4 has already been played"
emotion_data = """sad(11%) neutral(80%) 
neutral(41%) sad(46%) 
sad(14%) neutral(80%) 
happy(78%) 
happy(36%) neutral(59%) 
Here are uh my cards"""

if not API_KEY:
    print("Error: OTIS environment variable not found. Did you create your .env file?")
else:
    basic_query = (f"""Is this player bluffing? Move: {move} Game State: {state} Emotion Data: {emotion_data} """)
    
    # System prompt provides context and persona (Otis the Cheat player)
    system_prompt = """Your name is Otis. You are playing the card game Cheat. It is your job to determine whether the player is bluffing or not.
You will be given the following information: the player's true move, the state of the game, and information about the player: Facial Emotion Recognition & voice to text data.
The format of the data is the last five readings of FER followed by the latest recorded spoken sentence of the player.
The aim of the player is to get rid of all of their cards, and they may lie.
Base your decision on the game state and the player's emotional data."""

    # Get the structured schema
    cheat_schema = get_cheat_analysis_schema()

    # Call the function, passing the schema
    result_text = generate_content(
        prompt=basic_query, 
        api_key=API_KEY, 
        system_prompt=system_prompt,
        response_schema=cheat_schema # <-- This is the new parameter
    )
    
    print("\n--- Model Response (Guaranteed JSON Format) ---")
    
    # Try to parse and pretty-print the JSON response for readability
    try:
        parsed_json = json.loads(result_text)
        print(json.dumps(parsed_json, indent=4))
    except json.JSONDecodeError:
        print("Raw text (could not parse as JSON):")
        print(result_text)
        
    print("---------------------------------------------")
