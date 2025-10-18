import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("OTIS") 
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
MODEL_NAME = "gemini-2.5-flash-preview-09-2025" 


def get_cheat_analysis_schema():
    """
    Defines the structured output schema for the Cheat game analysis 
    (bluff detection).
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


def get_move_schema():
    """
    Defines the structured output schema for the Move planning.
    """
    return {
        "type": "OBJECT",
        "properties": {
            "SuggestedCardRank": {
                "type": "STRING",
                "description": "The rank of the card the AI should announce it's playing (e.g., 'A', '2', 'K')."
            },
            "CardsToPlay": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "A list of the actual cards from the player's hand to play (e.g., ['2S', '2H']). This must be a subset of the 'hand' provided in the prompt."
            },
            "Reasoning": {
                "type": "STRING",
                "description": "A concise explanation (2-3 sentences) for the suggested move, considering bluffing potential and game strategy."
            }
        },
        "propertyOrdering": ["SuggestedCardRank", "CardsToPlay", "Reasoning"],
        "required": ["SuggestedCardRank", "CardsToPlay", "Reasoning"]
    }



def generate_content(prompt, api_key, system_prompt=None, response_schema=None):
    """
    Sends a prompt to the Gemini API and returns the generated text.
    Includes support for guaranteed structured JSON output and retries.

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
        payload["config"] = {
            "systemInstruction": system_prompt
        }

    if response_schema:
        if "config" not in payload:
             payload["config"] = {}
             
        payload["config"]["responseMimeType"] = "application/json"
        payload["config"]["responseSchema"] = response_schema
        
    full_url = f"{API_URL}?key={api_key}"
    
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


def analyze_bluff(move: str, state: str, emotion_data: str) -> dict:
    """
    Determines if an opponent is bluffing based on their move, 
    the game state, and emotional data.
    
    Args:
        move (str): The opponent's announced move (e.g., "Player 1 has played 2 4s").
        state (str): The current game state (e.g., "1 4 has already been played").
        emotion_data (str): Facial Emotion Recognition and voice-to-text data.

    Returns:
        dict: A dictionary containing 'Bluffing' (bool) and 'Reasoning' (str).
    """
    if not API_KEY:
        return {"Error": "API Key is missing."}

    basic_query = (
        f"Is this player bluffing? Move: {move} Game State: {state} Emotion Data: {emotion_data}"
    )
    
    system_prompt = (
        "Your name is Otis. You are playing the card game Cheat. It is your job to determine whether the "
        "player is bluffing or not. You will be given the player's move, the state of the game, "
        "and data on the player (Facial Emotion Recognition & voice-to-text). "
        "Base your decision on the game state and the player's emotional data and return a JSON object."
    )

    result_text = generate_content(
        prompt=basic_query, 
        api_key=API_KEY, 
        system_prompt=system_prompt,
        response_schema=get_cheat_analysis_schema()
    )
    
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"Error": "Could not parse API response as JSON.", "Raw_Response": result_text}


def move(hand: list, state: str) -> dict:
    """
    Suggests the best move (cards to play and rank to announce) for the AI.

    Args:
        hand (list): The AI's current hand (e.g., ['2S', '4D', '4H', 'JS', 'KD']).
        state (str): The current game state (e.g., "The required rank is 4. The pile is 10 cards deep.").

    Returns:
        dict: A dictionary containing 'SuggestedCardRank', 'CardsToPlay', and 'Reasoning'.
    """
    if not API_KEY:
        return {"Error": "API Key is missing."}
        
    hand_str = ", ".join(hand)

    basic_query = (
        f"You are playing the card game Cheat, you'd like to win. Your hand is: {hand_str}. "
        f"The current game state is: {state}. What is the best move to make right now? "
        "What rank are you announcing, and what actual cards will you play from your hand. You can bluff."
    )
    
    system_prompt = (
        "You are Otis, an expert Cheat player. Your goal is to get rid of all your cards. "
        "Analyze the hand and game state to determine the most strategic move, "
        "including whether to play cards that match the required rank or to bluff. "
        "The suggested move MUST be a list of cards that exist in the provided hand. "
        "Return the decision as a JSON object."
    )

    result_text = generate_content(
        prompt=basic_query, 
        api_key=API_KEY, 
        system_prompt=system_prompt,
        response_schema=get_move_schema()
    )
    
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"Error": "Could not parse API response as JSON.", "Raw_Response": result_text}


# analysis_result = analyze_bluff(move, state, emotion_data)
# move_result = move(hand, state)