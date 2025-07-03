import os
import json
import sys
from dotenv import load_dotenv
import google.generativeai as genai
import google.api_core.exceptions


# --- Configuration ---
STATS_FILE = "persona_stats.json"
MODEL_NAME = "gemini-1.5-flash-latest"


def main():
    """Main function that orchestrates the Persona 5 life sim application."""
    # Initialize API
    if not initialize_gemini_api():
        return
    
    # Load and display current stats
    current_stats = load_stats()
    display_stats(current_stats)
    
    # Get user input
    try:
        task = input("\nEnter your log of the day to determine stat increase: ")
        if not task.strip():
            print("No activity logged. Exiting.")
            return
    except KeyboardInterrupt:
        print("\nExiting...")
        return
    
    # Evaluate with AI and update stats
    updated_stats = evaluate_and_update_stats(task, current_stats)
    
    # Save and display final stats
    save_stats(updated_stats)
    display_stats(updated_stats)
    print("\nSession complete. Your stats have been updated!")


def initialize_gemini_api():
    """Initialize the Gemini API with the API key from environment variables.
    
    Returns:
        bool: True if initialization successful, False otherwise.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        print("Please ensure your .env file contains: GEMINI_API_KEY=\"YOUR_ACTUAL_API_KEY\"")
        return False
    
    try:
        genai.configure(api_key=api_key)
        # Test model initialization
        model = genai.GenerativeModel(MODEL_NAME)
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        print("Your API key might be invalid or there's an issue with the configuration.")
        return False


def load_stats():
    """Load stats from STATS_FILE or initialize them if the file doesn't exist.
    
    Returns:
        dict: Dictionary containing the five persona stats.
    """
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
                # Ensure all default stats exist in the loaded data
                for stat, default_val in default_stats.items():
                    if stat not in current_stats:
                        current_stats[stat] = default_val
                return current_stats
        except (json.JSONDecodeError, IOError):
            print(f"Warning: {STATS_FILE} is corrupted. Starting with default stats.")
            return default_stats
    else:
        print(f"No existing stats found. Creating {STATS_FILE} with default stats.")
        return default_stats


def save_stats(stats):
    """Save the current stats dictionary to STATS_FILE.
    
    Args:
        stats (dict): Dictionary containing the persona stats to save.
        
    Returns:
        bool: True if save successful, False otherwise.
    """
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
        print(f"Stats saved to {STATS_FILE}")
        return True
    except IOError as e:
        print(f"Error saving stats to {STATS_FILE}: {e}")
        return False


def evaluate_and_update_stats(activity_log, current_stats):
    """Evaluate the activity log using AI and update stats accordingly.
    
    Args:
        activity_log (str): The user's daily activity log.
        current_stats (dict): Current persona stats.
        
    Returns:
        dict: Updated stats dictionary.
    """
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
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(f"{system_prompt}\nUser log: {activity_log}")
        raw_ai_output = response.text.strip()
        
        print("\n--- AI Evaluation Result ---")
        print(raw_ai_output)
        print("--------------------------")
        
        # Parse and apply stat updates
        updated_stats = parse_and_apply_stat_updates(raw_ai_output, current_stats.copy())
        return updated_stats
        
    except google.api_core.exceptions.ClientError as e:
        print(f"\nAn API error occurred: {e}")
        handle_api_error(e)
        return current_stats
    except Exception as e:
        print(f"\nAn unexpected error occurred during AI evaluation: {e}")
        return current_stats


def parse_and_apply_stat_updates(ai_output, stats):
    """Parse AI output and apply stat updates.
    
    Args:
        ai_output (str): Raw output from AI evaluation.
        stats (dict): Current stats dictionary to update.
        
    Returns:
        dict: Updated stats dictionary.
    """
    lines = ai_output.split('\n')
    updated_any_stat = False
    
    for line in lines:
        line = line.strip()
        if '=' in line:
            try:
                stat_name, points_str = line.split('=', 1)
                stat_name = stat_name.strip()
                points = int(points_str.strip())
                
                if stat_name in stats:
                    stats[stat_name] += points
                    print(f"Updated {stat_name}: +{points} points.")
                    updated_any_stat = True
                else:
                    print(f"Warning: AI suggested unknown stat '{stat_name}'. Skipping.")
            except ValueError:
                print(f"Warning: Could not parse line '{line}'. Skipping.")
        else:
            if line:  # Only print if line is not empty
                print(f"Info: {line}")
    
    if not updated_any_stat:
        print("No valid stat updates were parsed from AI's response.")
    
    return stats


def display_stats(stats):
    """Display the current stats in a readable format.
    
    Args:
        stats (dict): Dictionary containing the persona stats to display.
    """
    print("\n--- Current Persona Stats ---")
    for stat, value in stats.items():
        print(f"{stat}: {value}")
    print("---------------------------")


def handle_api_error(error):
    """Handle different types of API errors with appropriate messages.
    
    Args:
        error: The API error exception.
    """
    error_str = str(error)
    
    if "RESOURCE_EXHAUSTED" in error_str:
        print("You might have hit a rate limit. Wait a bit and try again.")
    elif "PERMISSION_DENIED" in error_str or "API key not valid" in error_str:
        print("Your API key might have issues. Verify permissions in Google AI Studio.")
    elif "model is not found" in error_str or "not supported" in error_str:
        print(f"The model '{MODEL_NAME}' might no longer be available.")
        print("Run `apicheck.py` to see available models.")
    else:
        print("Please check your API key, network connection, or try again later.")


if __name__ == "__main__":
    main()
