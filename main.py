import os
import openai
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Function to get response from OpenAI
def get_openai_response(message):
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are NotPlaylist, an AI chatbot adept in creating Spotify music playlists."},
                {"role": "user", "content": message}
            ],
            timeout=10
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error during OpenAI API call: {e}")
        return "An error occurred with OpenAI."

# Function to authenticate with Spotify
def spotify_authenticate():
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE
        )
        return auth_manager
    except Exception as e:
        logger.error(f"Error during Spotify authentication: {e}")
        return None

# Function to create a Spotify playlist
def create_playlist(sp, user_id, playlist_name):
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,
            collaborative=False,
            description=''
        )
        return playlist['id']
    except Exception as e:
        logger.error(f"Error creating Spotify playlist: {e}")
        return None

# Flask route for the Spotify OAuth callback
@app.route('/spotify_callback')
def spotify_callback():
    logger.info("Received Spotify callback")
    auth_manager = spotify_authenticate()
    if not auth_manager:
        return "Error in Spotify authentication."
    code = request.args.get('code')
    token_info = auth_manager.get_access_token(code)
    session['spotify_token'] = token_info['access_token']
    return redirect('https://t.me/TgAzTranslatorTest_bot')

# Flask route for the index page, can be used for health checks
@app.route('/')
def index():
    logger.info("Index route accessed")
    return 'The Flask server is running!'

# Start command handler
def start(update: Update, context: CallbackContext):
    logger.info("Start command received")
    auth_manager = spotify_authenticate()
    if not auth_manager:
        update.message.reply_text("Error in Spotify authentication.")
        return
    auth_url = auth_manager.get_authorize_url()
    update.message.reply_text(f"Please authenticate with Spotify here: {auth_url}")

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
                update.message.reply_text(f"Playlist '{playlist_name}' created with ID:{playlist_id}")
            else:
                update.message.reply_text("You must authenticate with Spotify first. Send '/start' to get the authentication link.")
    else:
        openai_response = get_openai_response(user_message)
        update.message.reply_text(openai_response)

# Initialize and run the bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

# Start the Telegram bot polling
updater.start_polling()
updater.idle()

