import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

MAX_NOTE_LENGTH = 200
MAX_AMOUNT = 10_000_000