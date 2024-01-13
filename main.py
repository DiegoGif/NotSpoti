import os
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Function to get response from OpenAI
def get_openai_response(message):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are NotPlaylist, an AI chatbot adept in creating Spotify music playlists."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# Function to authenticate with Spotify
def spotify_authenticate():
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    )
    return auth_manager  # Return the auth_manager instead of the Spotify client

# Function to create a Spotify playlist
def create_playlist(sp, user_id, playlist_name):
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        collaborative=False,
        description=''
    )
    return playlist['id']

# Start command handler
def start(update: Update, context: CallbackContext):
    auth_manager = spotify_authenticate()
    auth_url = auth_manager.get_authorize_url()
    update.message.reply_text(f"Please authenticate with Spotify here:{auth_url}")

# Message handler
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    if user_message.startswith('playlist'):
        command, *params = user_message.split()
        if command == 'playlist_create':
            if 'spotify_token' in context.user_data:
                sp = spotipy.Spotify(auth=context.user_data['spotify_token'])
                user_id = sp.current_user()['id']
                playlist_name = ' '.join(params)
                playlist_id = create_playlist(sp, user_id, playlist_name)
                openai_response = get_openai_response(user_message)
                # Additional logic to parse song list and add songs to playlist goes here
                update.message.reply_text(f"Playlist '{playlist_name}' created with ID: {playlist_id}")
            else:
                update.message.reply_text("You must authenticate with Spotify first. Send '/start' to get the authentication link.")
    else:
        openai_response = get_openai_response(user_message)
        update.message.reply_text(openai_response)

# Initialize and run the bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
updater.start_polling()
updater.idle()
