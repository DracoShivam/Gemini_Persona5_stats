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


![image](https://github.com/user-attachments/assets/37da5718-b4d7-4705-a324-3e99b770fd18)
