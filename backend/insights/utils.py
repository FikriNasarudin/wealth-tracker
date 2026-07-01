import requests
import json
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
# Fallback to localhost if not running in docker
# A robust approach could check environment variables.
# OLLAMA_MODEL = "phi3" # Wait, the user can choose. We'll set a default or use an env variable.
import os
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3")

def generate_financial_insights(dashboard_type, data_context):
    """
    Calls the local Ollama API to generate insights based on the provided data context.
    Returns a dictionary with 'health_score' and 'recommendations'.
    """
    system_prompt = f"""You are an elite, strict personal financial advisor. 
You are analyzing the user's '{dashboard_type}' dashboard.
You must return your response EXACTLY as a raw JSON object with no markdown formatting, no backticks, and no extra text.
The JSON must have this exact structure:
{{
  "health_score": "A string representing a grade like A+, B-, C, or a number out of 100",
  "recommendations": [
    "Actionable insight 1",
    "Actionable insight 2",
    "Actionable insight 3"
  ]
}}
"""
    prompt = f"Here is the user's current financial data for this month:\n{json.dumps(data_context, indent=2)}\n\nPlease provide the health score and recommendations based on this data."

    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }

    try:
        # First try localhost, then host.docker.internal
        url = "http://localhost:11434/api/generate"
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            url = "http://host.docker.internal:11434/api/generate"
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

        result = response.json()
        response_text = result.get('response', '')
        
        # Parse JSON
        parsed = json.loads(response_text)
        return parsed
    except Exception as e:
        logger.error(f"Error calling Ollama API: {e}")
        # Return graceful fallback
        return {
            "health_score": "N/A",
            "recommendations": [
                "Unable to connect to the local AI advisor (Ollama).",
                "Please ensure Ollama is installed and running on your machine.",
                f"Run 'ollama run {OLLAMA_MODEL}' in your terminal to start the AI."
            ]
        }
