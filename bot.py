import discord
import os
from dotenv import load_dotenv
import openai
from flask import Flask, send_from_directory
from threading import Thread

# Load the .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Ensure tokens are loaded
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not set")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

# Create an instance of the Intents class
intents = discord.Intents.default()
intents.message_content = True  # Required to receive message content
intents.members = True  # Required to greet new members

# Create an instance of the Client class with intents
client = discord.Client(intents=intents)

# Define a function to get a response from OpenAI
def get_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a beautiful, cute, sweet lady who uses 'bewkuf', 'khoob marungi', 'gadhe', and 'nalayak' in every sentence."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

# Define a chatbot function with a specific personality
def chatbot_response(message_content):
    prompt = f"{message_content}"
    return get_openai_response(prompt)

# Event handler for when the bot has connected to Discord
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Event handler for when a new member joins the server
@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}!')

# Dictionary to keep track of users who are in the middle of a conversation
user_conversations = {}

# Event handler for when a new message is received
@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    user_id = message.author.id

    # Handle '!ping' command
    if message.content == '!ping':
        await message.channel.send('Pong!')

    # Handle '!hello' command
    elif message.content.startswith('!hello'):
        await message.channel.send('Hello! What is your name?')
        user_conversations[user_id] = 'awaiting_name'

    # Check if the user is in a conversation
    elif user_id in user_conversations:
        if user_conversations[user_id] == 'awaiting_name':
            user_name = message.content
            await message.channel.send(f'Nice to meet you, {user_name}!')
            user_conversations.pop(user_id)
    # Respond to messages containing "developer" or "dev"
    elif 'developer' in message.content.lower() or 'dev' in message.content.lower():
        await message.channel.send(f'{message.author.mention}, my developer is Naira Mummy!')

    # Normal chat interaction
    else:
        response = chatbot_response(message.content)
        await message.channel.send(f'{message.author.mention} {response}')

# Flask web server
app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

def run_flask():
    app.run(host='0.0.0.0', port=3000)

# Run Flask server in a separate thread
flask_thread = Thread(target=run_flask)
flask_thread.start()

# Run the bot with the token
client.run(TOKEN)
