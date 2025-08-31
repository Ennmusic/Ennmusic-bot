from pyrogram import Client
from pyrogram.types import Message

API_ID = int(input("Enter API_ID: "))
API_HASH = input("Enter API_HASH: ")

with Client(name="assistant", api_id=API_ID, api_hash=API_HASH) as app:
    print("\nHere is your SESSION_STRING:\n")
    print(app.export_session_string())
