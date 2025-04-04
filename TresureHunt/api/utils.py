from functools import lru_cache
import httpx
from .config import settings
from typing import Optional
import logging
import json
import asyncio
import random
from difflib import SequenceMatcher
from .clues1 import bonus_challenges
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import os
import httpx
import asyncio
import logging

# New function to query the Fireworks Chat model endpoint
async def ask_fireworks_chat_async(prompt: str) -> str:
    API_URL = "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "model": "accounts/fireworks/models/deepseek-v3-0324"
    }
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                # Expecting a structure like: {"choices": [{"message": ...}]}
                if "choices" in data and len(data["choices"]) > 0 and "message" in data["choices"][0]:
                    return data["choices"][0]["message"]
                return "No response found"
            else:
                logging.error(f"Fireworks API Error: Status {response.status_code}, Response: {response.text}")
                return "Error: API call failed."
    except Exception as e:
        logging.error(f"Exception with Fireworks API: {str(e)}")
        return "Error: Exception occurred."



def fallback_verification(prompt: str) -> str:
    """Robust fallback verification."""
    try:
        # Normalize input
        prompt = prompt.lower().replace('"', "'")
        # Extract answers
        correct = ""
        team = ""
        if "correct answer" in prompt and "team answer" in prompt:
            parts = prompt.split("team answer")
            correct_part = parts[0].split("correct answer")[-1]
            team_part = parts[1]
            correct = correct_part.split("'")[1] if "'" in correct_part else ""
            team = team_part.split("'")[1] if "'" in team_part else ""
        # Clean and compare
        correct = correct.strip().upper()
        team = team.strip().upper()
        if correct and team:
            return "The answer is correct." if correct == team else "The answer is incorrect."
        return "Unable to verify the answer."
    except Exception as e:
        logging.error(f"Fallback verification error: {str(e)}")
        return "Unable to verify the answer."

def calculate_average_solve_time(team_id: str, team_timers: dict) -> Optional[float]:
    """Calculate average solve time for a team."""
    if team_id not in team_timers or "history" not in team_timers[team_id]:
        return None
    times = team_timers[team_id]["history"]
    return sum(times) / len(times) if times else None

async def generate_bonus_challenge(team_id: str) -> dict:
    """Select a random static bonus challenge."""
    try:
        challenge = random.choice(bonus_challenges)
        return {
            "question": challenge["question"],
            "answer": challenge["answer"],
            "points": challenge["points"],
            "is_dynamic": False
        }
    except Exception as e:
        logging.error(f"Bonus challenge selection failed: {str(e)}")
        return {
            "question": "What year was Python first released?",
            "answer": "1991",
            "points": 50,
            "is_dynamic": False
        }

async def generate_congrats_message(team_id: str, clue_id: int) -> str:
    """Generate an AI-powered congratulatory message using GPT-Neo."""
    prompt = (f"Write one sentence congratulating team {team_id} for solving "
              f"clue {clue_id} in a treasure hunt. Be creative but brief.")
    response = await ask_fireworks_chat_async(prompt)
    return response if response else "Great job! On to the next challenge!"

async def verify_answer_hybrid(correct_answer: str, team_answer: str) -> bool:
    """Tiered verification approach for answers."""
    # Tier 1: Strict match
    if team_answer.lower().strip() == correct_answer.lower().strip():
        return True
        
    # Tier 2: Close match (handles minor typos)
    if len(team_answer) > 3 and SequenceMatcher(
        None, team_answer.lower(), correct_answer.lower()
    ).ratio() > 0.8:
        return True
        
    # Tier 3: LLM verification (only if first two fail)
    try:
        prompt = (
            f"Verify if these mean the same (respond with ONLY 'yes' or 'no'):\n"
            f"Correct: '{correct_answer}'\n"
            f"Given: '{team_answer}'"
        )
        response = await ask_fireworks_chat_async(prompt)
        return response.lower().strip().startswith('y')
    except Exception:
        return False  # Final fallback
