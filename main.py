
import os
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Fetching the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# OpenAI Function
def get_openai_response(message, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": message}]
    )
    return response['choices'][0]['message']['content']

# Spotify Functions
def spotify_authenticate(client_id, client_secret, redirect_uri, scope):
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def create_playlist(sp, user_id, playlist_name, public=True, collaborative=False, description=''):
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=public,
        collaborative=collaborative,
        description=description
    )
    return playlist['id']

# Telegram Bot Handlers
def start(update: Update, context: CallbackContext):
    auth_manager = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI,
                                scope=SPOTIFY_SCOPE)
    auth_url = auth_manager.get_authorize_url()
    update.message.reply_text(f"Please authenticate with Spotify here: {auth_url}")

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
                update.message.reply_text(f"Playlist '{playlist_name}' created with ID: {playlist_id}")
            else:
                update.message.reply_text("You must authenticate with Spotify first. Send '/start' to get the authentication link.")
    else:
        openai_response = get_openai_response(user_message, OPENAI_API_KEY)
        update.message.reply_text(openai_response)

# Bot Initialization
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
updater.start_polling()
updater.idle()
