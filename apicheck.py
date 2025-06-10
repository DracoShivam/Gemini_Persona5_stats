import os
from dotenv import load_dotenv
import google.generativeai as genai
import google.api_core.exceptions # Import for ClientError and NotFound exceptions

# Load .env to get GEMINI_API_KEY
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- Configuration ---
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

# --- Check Access ---
print("Attempting to list available Gemini models...")
# We'll explicitly look for models recommended by the error, or other capable models
target_models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro" # Keep this as a fallback for older accounts, though less likely now
]
found_compatible_model = None

try:
    available_models = list(genai.list_models()) # Get all models once

    for target_name in target_models:
        for m in available_models:
            # Check for the exact target name in the model name, and it supports content generation
            if target_name in m.name and 'generateContent' in m.supported_generation_methods:
                print(f"Access to compatible model found: {m.name}")
                found_compatible_model = m.name
                break # Found a suitable model, no need to check other 'm'
        if found_compatible_model:
            break # Found a suitable model, no need to check other 'target_name'

    if not found_compatible_model:
        print("Your API key does NOT appear to have access to any of the recommended or common Gemini models for text generation.")
        print("Tried to find: " + ", ".join(target_models))
        print("Available models:")
        for m in available_models:
            print(f"- {m.name} (Methods: {m.supported_generation_methods})")
        print("\nPossible reasons for no access:")
        print("1. Your API key is incorrect or expired.")
        print("2. You might not have been granted access to newer models.")
        print("3. Check the Google AI Studio for your API key and its associated access.")
        print("4. There might be region restrictions or a temporary service issue.")

except google.api_core.exceptions.ClientError as e:
    print(f"\nAPI call failed with error: {e}")
    if "API key not valid" in str(e):
        print("This strongly suggests your API key is invalid.")
    elif "RESOURCE_EXHAUSTED" in str(e):
        print("You've likely hit a rate limit. Try again in a few minutes.")
    elif "PERMISSION_DENIED" in str(e):
        print("Your API key might not have the necessary permissions for `list_models` or `generateContent`.")
        print("Check your API key restrictions in Google AI Studio.")
    else:
        print("An unexpected client error occurred.")
except Exception as e:
    print(f"\nAn unexpected error occurred during model listing: {e}")
    print("This could be a network issue or another problem.")

print("\n--- Test a simple Gemini API call (if a compatible model was found) ---")
if found_compatible_model:
    try:
        # Use the actual model name that was found!
        model = genai.GenerativeModel(found_compatible_model)
        response = model.generate_content("Hello, Gemini!")
        print(f"Simple call to '{found_compatible_model}' successful!")
        print(f"Response (first 50 chars): {response.text[:50]}...")
        print("Your API key is active and has access to a compatible Gemini model for text generation.")
    except google.api_core.exceptions.NotFound as e:
        print(f"Error: The model '{found_compatible_model}' could not be found or is not supported for text generation.")
        print(f"Details: {e}")
    except google.api_core.exceptions.ClientError as e:
        print(f"Failed to make a simple call to {found_compatible_model}: {e}")
        if "PERMISSION_DENIED" in str(e) or "API key not valid" in str(e):
            print("Even though 'list_models' might work, direct content generation might have stricter permissions or an invalid key.")
        elif "INVALID_ARGUMENT" in str(e):
            print("There might be an issue with the arguments provided to `generate_content` for this specific model.")
        else:
            print("An unexpected client error occurred during content generation.")
    except Exception as e:
        print(f"An unexpected error occurred during the simple Gemini API call: {e}")
else:
    print("No suitable Gemini model was found to test content generation. Please check your API key and access in Google AI Studio.")