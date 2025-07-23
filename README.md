# Werewolf LLM Project

This project simulates the classic social deduction game "Werewolf" using LLM (Large Language Model) agents. Each player is controlled by an LLM (mocked by default), and the entire game process is recorded, including role assignment, speeches, voting, and deaths.

## Project Structure

- `main.py` - Entry point, sets up and runs the game
- `game_engine.py` - Game engine and flow control
- `player_agent.py` - Player and LLM agent logic
- `roles.py` - Role definitions
- `logger.py` - Structured game logging
- `llm_api.py` - LLM API interface (mocked, can be replaced with real API)
- `requirements.txt` - Dependencies
- `README.md` - Project documentation

## How to Run

1. Make sure you have Python 3.7+ installed.
2. (Optional) Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```
4. After the game finishes, check `game_log.json` for the full game log.

## Customization & Extension

- To use a real LLM API, implement `call_llm_api` in `llm_api.py` with your provider (e.g., OpenAI, Qwen, etc.).
- You can adjust the number of players and role distribution in `main.py`.
- Extend roles and actions in `roles.py` and `game_engine.py` for more complex gameplay.
- The log structure is JSON and can be used for visualization or analysis.

## License
MIT

