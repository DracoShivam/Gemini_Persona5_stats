# Persona 5-Inspired Life Sim App

This is a text-based life simulation application inspired by the social stat system in Persona 5. Users can log their daily activities, and an AI evaluator will interpret these logs to determine which character stats are developed, awarding points accordingly. All stat progress is saved persistently.

## Features

* **Daily Activity Logging:** Describe your day's actions in a journal-style entry.
* **AI Stat Evaluation:** Leveraging the Gemini API, the app intelligently assesses your activities and assigns points to relevant stats.
* **Five Core Stats:** Track your progress across:
    * **Knowledge:** Represents academic prowess and intellectual growth.
    * **Charm:** Reflects your social grace and attractiveness.
    * **Guts:** Measures your courage and resilience.
    * **Health:** Indicates your physical well-being and stamina.
    * **Kindness:** Shows your compassion and helpfulness towards others.
* **Persistent Stat Storage:** All your stat progress is saved to a local `persona_stats.json` file, so your growth is never lost between sessions.
* **Dynamic Stat Gains:** Points awarded (1, 2, or 3) are based on the effort level described in your daily log.

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the main program:
```bash
python project.py
```

The app will:
1. Load your current stats (or create new ones if first time)
2. Display your current progress
3. Prompt you to enter your daily activity log
4. Send your log to the AI for evaluation
5. Update your stats based on the AI's assessment
6. Save your progress for future sessions

## Testing

Run the test suite with pytest:
```bash
pytest test_project.py
```

Or run with verbose output:
```bash
pytest test_project.py -v
```

## Project Structure

```
.
├── project.py              # Main application file
├── test_project.py         # Test suite
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                   # API key (you need to create this)
├── .gitignore             # Git ignore file
└── persona_stats.json     # Stat storage (created automatically)
```

## Functions

### Main Functions (in project.py)

1. **`main()`** - Orchestrates the entire application flow
2. **`initialize_gemini_api()`** - Sets up the Gemini API connection
3. **`load_stats()`** - Loads existing stats or creates defaults
4. **`save_stats(stats)`** - Saves stat progress to file
5. **`evaluate_and_update_stats(activity_log, current_stats)`** - Processes user input with AI
6. **`parse_and_apply_stat_updates(ai_output, stats)`** - Parses AI response and updates stats
7. **`display_stats(stats)`** - Shows current stat values
8. **`handle_api_error(error)`** - Handles various API errors gracefully

### Testing

The test suite includes comprehensive tests for:
- Loading and saving stats
- Parsing AI output
- Error handling
- Edge cases and invalid inputs
- File I/O operations

## API Key Setup

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add it to your `.env` file as shown above
4. Ensure the API key has access to the Gemini models

## Error Handling

The application handles various error scenarios:
- Missing or invalid API keys
- Network connectivity issues
- Rate limiting
- Corrupted stat files
- Invalid AI responses

## Example Usage

```
--- Current Persona Stats ---
Knowledge: 5
Charm: 3
Guts: 2
Health: 4
Kindness: 1
---------------------------

Enter your log of the day to determine stat increase: Today I studied advanced calculus for 3 hours and helped my neighbor with their computer problems.

--- Sending log to AI for evaluation... ---

--- AI Evaluation Result ---
Knowledge = 3
Kindness = 2
--------------------------
Updated Knowledge: +3 points.
Updated Kindness: +2 points.
Stats saved to persona_stats.json

--- Current Persona Stats ---
Knowledge: 8
Charm: 3
Guts: 2
Health: 4
Kindness: 3
---------------------------

Session complete. Your stats have been updated!
```

## License

This project is created for educational purposes as part of CS50's Introduction to Programming with Python.
