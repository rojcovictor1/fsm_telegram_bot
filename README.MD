# Telegram Bot Project with FSM

This project is a simple Telegram bot implemented using the aiogram library. The bot allows users to fill out a form, save their data, and view the saved data through commands.

## Features

- Fill out a form with personal details
- Save user data
- View saved user data
- Basic error handling and state management

## Requirements

- Python 3.7+
- `aiogram` library

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/rojcovictor1/fsm_telegram_bot.git
    cd fsm_telegram_bot
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the environment variables:**

    - Copy the `.env.example` file to `.env`:

    ```sh
    cp .env.example .env
    ```

    - Edit the `.env` file to include your Telegram bot token:

    ```env
    BOT_TOKEN=your-telegram-bot-token
    ```

## Usage

Run the bot with the following command:

```sh
python main.py
```

## File Descriptions

main.py
This is the main script for the bot. It includes the handlers for commands and messages, state management, and running the polling.

.env.example
This file provides an example of the environment variables needed for the bot. You should copy this file to .env and fill in your actual bot token.

requirements.txt
This file lists all the dependencies required for the project.

## Project Overview
The bot allows users to fill out a form by responding to prompts. The collected data is stored in a dictionary and can be retrieved with the /showdata command. If a user tries to view their data without having filled out the form, they will be prompted to start the form with the /fillform command.

## Handlers in main.py:
- /start command: Initiates the form filling process.
- /cancel command: Cancels the current operation and exits the state machine.
- /showdata command: Shows the stored data of the user or prompts the user to fill out the form if no data is available.
- Fallback handler: Replies with a generic message for unrecognized input.
The bot uses the aiogram library for asynchronous operations and state management.