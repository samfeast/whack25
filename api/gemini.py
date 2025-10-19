import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuration ---
# 1. Load environment variables
load_dotenv()

# The genai.Client() will automatically look for the API key in the
# GEMINI_API_KEY or GOOGLE_API_KEY environment variables.
# For best practice, we'll map your custom "OTIS" key to the standard environment variable.
# NOTE: You should change 'OTIS' to 'GEMINI_API_KEY' in your .env file for true best practice.
try:
    API_KEY = os.getenv("OTIS")
    if API_KEY:
        os.environ["GEMINI_API_KEY"] = API_KEY
    
    # 2. Initialize the client (handles authentication, URL, etc.)
    client = genai.Client()
    
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

# Model name is now just the ID, no need for the full URL path
MODEL_NAME = "gemini-2.5-flash"


# --- Schemas (Using types.Schema for the SDK) ---

def get_cheat_analysis_schema() -> types.Schema:
    """
    Defines the structured output schema for the Cheat game analysis 
    (bluff detection).
    """
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Bluffing": types.Schema(
                type=types.Type.BOOLEAN,
                description="True if the player is likely bluffing, False otherwise."
            ),
            "Reasoning": types.Schema(
                type=types.Type.STRING,
                description="A 3-sentence summary of why this decision was made, analyzing the game state and emotion data."
            ),
        },
        required=["Bluffing", "Reasoning"]
    )


def get_move_schema() -> types.Schema:
    """
    Defines the structured output schema for the Move planning.
    """
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "SuggestedCardRank": types.Schema(
                type=types.Type.STRING,
                description="The rank of the card the AI should announce it's playing (e.g., 'A', '2', 'K')."
            ),
            "CardsToPlay": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="A list of the actual cards from the player's hand to play (e.g., ['2S', '2H']). This must be a subset of the 'hand' provided in the prompt."
            ),
            "Reasoning": types.Schema(
                type=types.Type.STRING,
                description="A concise explanation (2-3 sentences) for the suggested move, considering bluffing potential and game strategy."
            ),
        },
        required=["SuggestedCardRank", "CardsToPlay", "Reasoning"]
    )


# --- Core API Call Function (Simplified) ---

def generate_content_sdk(prompt: str, system_prompt: str, response_schema: types.Schema) -> dict | str:
    """
    Sends a prompt to the Gemini API using the official SDK.
    The SDK handles retries and API error decoding.

    Args:
        prompt: The main text prompt.
        system_prompt: Instructions for the model's behavior.
        response_schema: The schema for guaranteed JSON output.

    Returns:
        dict: The parsed JSON result, or a string error message.
    """
    if client is None:
        return "Error: Gemini client not initialized. Check your API key setup."

    try:
        # Configuration is now passed as a single object (GenerationConfig)
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt],
            config=config,
        )

        # The response.text is guaranteed to be valid JSON due to response_mime_type="application/json"
        return json.loads(response.text)

    except APIError as e:
        # SDK handles all 4xx/5xx errors and retries gracefully, raising APIError for final failures.
        return f"API Request Failed: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# --- Business Logic Functions (Simplified) ---

def analyze_bluff(move: str, state: str, emotion_data: str) -> dict:
    """
    Determines if an opponent is bluffing based on their move, 
    the game state, and emotional data.
    """
    basic_query = (
        f"Is this player bluffing? Move: {move} Game State: {state} Emotion Data: {emotion_data}"
    )
    
    system_prompt = (
        "Your name is Otis. You are playing the card game Cheat. It is your job to determine whether the "
        "player is bluffing or not. You will be given the player's move, the state of the game, "
        "and data on the player (Facial Emotion Recognition & voice-to-text). "
        "The data is the last 5 facial expression readings, as percentage confidence in up to seven emotions, "
        "with the 6th line holding the latest recorded sentence of speech. "
        "Base your decision on the game state and the player's emotional data and return a JSON object."
    )

    result = generate_content_sdk(
        prompt=basic_query, 
        system_prompt=system_prompt,
        response_schema=get_cheat_analysis_schema()
    )
    
    # Check if the result is an error string (type str) or the successful dict
    if isinstance(result, str):
        return {"Error": result}
    
    return result


def move(hand: list, state: str) -> dict:
    """
    Suggests the best move (cards to play and rank to announce) for the AI.
    """
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

    result = generate_content_sdk(
        prompt=basic_query, 
        system_prompt=system_prompt,
        response_schema=get_move_schema()
    )
    
    # Check if the result is an error string (type str) or the successful dict
    if isinstance(result, str):
        return {"Error": result}
        
    return result
