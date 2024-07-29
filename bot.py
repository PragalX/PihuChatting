import discord
import os
from dotenv import load_dotenv
import openai

# Load the .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Define a chatbot function with a specific personality
def chatbot_response(message_content):
    prompt = f"Respond to the following message in the style of a cute, caring, loving lady who uses 'bewkuf' in every sentence:\n\nMessage: {message_content}\nResponse:"
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

    # Normal chat interaction
    else:
        response = chatbot_response(message.content)
        await message.channel.send(response)

# Run the bot with the token
client.run(TOKEN)
