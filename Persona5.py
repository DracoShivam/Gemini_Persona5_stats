import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import google.api_core.exceptions

# --- Configuration ---
STATS_FILE = "persona_stats.json" # File to store stats permanently

# Load .env to get GEMINI_API_KEY
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    print("Please ensure your .env file contains: GEMINI_API_KEY=\"YOUR_ACTUAL_API_KEY\"")
    exit()

try:
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Your API key might be invalid or there's an issue with the configuration.")
    exit()

# Use the model name confirmed by your apicheck.py script
MODEL_NAME = "gemini-1.5-flash-latest"

try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"Error: Could not initialize model '{MODEL_NAME}'. Details: {e}")
    print("Please ensure you have access to this model via your API key.")
    exit()

# --- Stat Management Functions ---

def load_stats():
    """Loads stats from STATS_FILE or initializes them if the file doesn't exist."""
    default_stats = {
        "Knowledge": 0,
        "Charm": 0,
        "Guts": 0,
        "Health": 0,
        "Kindness": 0
    }
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                current_stats = json.load(f)
                # Ensure all default stats exist in the loaded data (for new stats added later)
                for stat, default_val in default_stats.items():
                    if stat not in current_stats:
                        current_stats[stat] = default_val
                return current_stats
        except json.JSONDecodeError:
            print(f"Warning: {STATS_FILE} is corrupted. Starting with default stats.")
            return default_stats
    else:
        print(f"No existing stats found. Creating {STATS_FILE} with default stats.")
        return default_stats

def save_stats(stats):
    """Saves the current stats dictionary to STATS_FILE."""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4) # indent for pretty-printing
        print(f"Stats saved to {STATS_FILE}")
    except IOError as e:
        print(f"Error saving stats to {STATS_FILE}: {e}")

def display_stats(stats):
    """Prints the current stats in a readable format."""
    print("\n--- Current Persona Stats ---")
    for stat, value in stats.items():
        print(f"{stat}: {value}")
    print("---------------------------")

# --- Main Application Logic ---

if __name__ == "__main__":
    current_persona_stats = load_stats()
    display_stats(current_persona_stats)

    task = input("\nEnter your log of the day to determine stat increase: ")

    # Gemini prompt template (from previous version, slightly refined)
    system_prompt = """
    You are an AI stat evaluator for a text-based life sim app inspired by Persona 5.
    The app tracks five stats: Knowledge, Charm, Guts, Health, Kindness.

    Based on the user's daily log, identify the **two stats** that were most developed.
    Award each of those two stats a point value based on the effort level:
    - 3 points: Outstanding / Expert-level effort
    - 2 points: Solid / Average-level effort
    - 1 point: Beginner / Basic effort

    Your output must strictly follow this format, with one stat per line:
    Stat = Points
    Stat = Points
    """

    print("\n--- Sending log to AI for evaluation... ---")
    try:
        response = model.generate_content(f"{system_prompt}\nUser log: {task}")
        raw_ai_output = response.text.strip()
        print("\n--- AI Evaluation Result ---")
        print(raw_ai_output)
        print("--------------------------")

        # --- Parse AI Output and Update Stats ---
        lines = raw_ai_output.split('\n')
        updated_any_stat = False
        for line in lines:
            line = line.strip()
            if '=' in line:
                try:
                    stat_name, points_str = line.split('=', 1)
                    stat_name = stat_name.strip()
                    points = int(points_str.strip())

                    if stat_name in current_persona_stats:
                        current_persona_stats[stat_name] += points
                        print(f"Updated {stat_name}: +{points} points.")
                        updated_any_stat = True
                    else:
                        print(f"Warning: AI suggested unknown stat '{stat_name}'. Skipping.")
                except ValueError:
                    print(f"Warning: Could not parse line '{line}'. Skipping.")
            else:
                if line: # Only print if line is not empty
                    print(f"Warning: Unexpected AI output line '{line}'. Skipping.")

        if not updated_any_stat:
            print("No valid stat updates were parsed from AI's response.")

    except google.api_core.exceptions.ClientError as e:
        print(f"\nAn API error occurred: {e}")
        print("Please check your API key, network connection, or try again later.")
        if "RESOURCE_EXHAUSTED" in str(e):
            print("You might have hit a rate limit. Wait a bit and try again.")
        elif "PERMISSION_DENIED" in str(e) or "API key not valid" in str(e):
            print("Your API key might have issues with generating content. Verify permissions in Google AI Studio.")
        elif "model is not found" in str(e) or "not supported" in str(e):
            print(f"The model '{MODEL_NAME}' might no longer be available or supported for this type of content generation.")
            print("Run `apicheck.py` again to see available models.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during AI evaluation: {e}")

    # --- Save and Display Updated Stats ---
    save_stats(current_persona_stats)
    display_stats(current_persona_stats)

    print("\nSession complete. Your stats have been updated!")