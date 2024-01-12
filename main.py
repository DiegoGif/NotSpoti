
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# OpenAI and Spotify Credentials
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "YOUR_SPOTIFY_REDIRECT_URI"
SPOTIFY_SCOPE = "playlist-modify-public playlist-modify-private"

# OpenAI Function
def get_openai_response(message, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=message,
        max_tokens=150
    )
    return response.choices[0].text.strip()

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
    update.message.reply_text("Welcome to the GPT-Spotify Bot!")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    if user_message.startswith('playlist'):
        command, *params = user_message.split()
        if command == 'playlist_create':
            playlist_name = ' '.join(params)
            sp = spotify_authenticate(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPE)
            user_id = sp.current_user()['id']
            playlist_id = create_playlist(sp, user_id, playlist_name)
            update.message.reply_text(f"Playlist '{playlist_name}' created with ID: {playlist_id}")
    else:
        openai_response = get_openai_response(user_message, OPENAI_API_KEY)
        update.message.reply_text(openai_response)

# Bot Initialization
telegram_bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
updater = Updater(token=telegram_bot_token, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
updater.start_polling()
updater.idle()
