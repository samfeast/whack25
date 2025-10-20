# CHEAiT

**AI Agent with Facial Emotion & Voice Recognition for the Bluffing Card Game "Cheat"**

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-EA4335?logo=google&logoColor=white)
![DeepFace](https://img.shields.io/badge/DeepFace-FER-FF6B6B)
![VOSK](https://img.shields.io/badge/VOSK-Voice%20Recognition-4CAF50)

[Devpost](https://devpost.com/software/cheait)
|
[WHACK 2025](https://whack-2025.devpost.com/)

## Overview

CHEAiT is an intelligent AI agent that plays the bluffing card game **Cheat**. Unlike traditional AI opponents, CHEAiT leverages **Facial Emotion Recognition (FER)** and **Voice Recognition** to analyze real-time player behavior and detect potential bluffing attempts. This multi-modal approach creates a more engaging and challenging gameplay experience.

In the card game Cheat, players take turns playing cards and claiming a rank (e.g., "three 5s"). The challenge is that you can play any cards you want—and other players must decide whether to believe you or call "Cheat!" If you're caught bluffing, you lose. If someone incorrectly accuses you, they lose.

## Features

- **Intelligent AI Agent** - Uses Google Gemini API for strategic decision-making
- **Facial Emotion Recognition** - Analyzes player facial expressions via DeepFace
- **Voice Recognition** - Captures and analyzes voice patterns using VOSK
- **Real-time Analysis** - Processes multimodal data during gameplay to inform bluff detection
- **WebSocket Game Server** - Supports multiplayer gameplay with live game state synchronization
- **Interactive React Frontend** - User-friendly interface for playing against the AI

## Setup

**Prerequisites:** Python 3.8+, Node.js 16+, npm or yarn


1. **Clone the repository**
   ```bash
   git clone https://github.com/samfeast/whack25.git
   cd whack25
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the VOSK Voice Model**
   - Download the English US model from: https://alphacephei.com/vosk/models
   - Extract to: `./client/vision/vosk-model-en-us-0.22/`
   ```bash
   # Example (Linux/Mac)
   wget "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
   unzip vosk-model-en-us-0.22.zip -d ./client/vision/
   ```

4. **Configure Gemini API Key**
   - Create a `.env` file in the project root
   - Add your Google Gemini API key:
   ```
   OTIS="your-gemini-api-key-here"
   ```
   - Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

5. **Start the backend server**
   ```bash
   cd api
   python main.py
   # or with gunicorn for production
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```
   The server will start at `http://localhost:8000`

6. **Install and start the frontend**
   ```bash
   cd client/frontend/my-app
   npm install
   npm start
   ```
   The app will open at `http://localhost:3000`


## Usage

### Starting a Game

1. Ensure both backend and frontend servers are running
2. Open the frontend at `http://localhost:3000`
3. Enter your username and join the game
4. The AI will analyze your emotions and voice patterns throughout the game
5. Make strategic decisions: play cards, call "Cheat," or bluff!

## How CHEAiT Detects Bluffing

CHEAiT uses three signals to inform its bluff detection strategy:

1. **Facial Expression Analysis** - Detects seven emotion states (angry, happy, sad, fear, surprise, disgust, neutral) using DeepFace
2. **Voice Patterns** - Analyzes voice recognition output and transcribed text using VOSK
3. **Game State Logic** - Considers the game state, remaining cards, and probability theory

The Gemini API synthesizes these signals to make informed decisions about whether to trust or challenge a player.

## Citation

```bibtex
@misc{cheait_WHACK2025,
  author       = {Feast, Sam and Nowak, Maks and Ryley, Oscar},
  title        = {CHEAiT: AI Agent with Facial Emotion and Voice Recognition for the Bluffing Card Game Cheat},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub Repository},
  howpublished = {\url{https://github.com/samfeast/whack25}},
  note         = {WHACK 2025 Hackathon Project}
}
```
