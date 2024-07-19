from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Token for accessing the Telegram bot


@dataclass
class Config:
    tg_bot: TgBot


# Create a function that reads the .env file and returns an instance
# of the Config class with the fields token and admin_ids populated
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))
