import os
import logging
# from telegram import Updat
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Environment variables
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
# SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
# SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
# SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
# TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Flask route for the Spotify OAuth callback
@app.route('/spotify_callback')
def spotify_callback():
    logger.info("Received Spotify callback")
    # Simulating successful callback
    return "Simulated Spotify callback success"

# Flask route for the index page, can be used for health checks
@app.route('/')
def index():
    logger.info("Index route accessed")
    return 'The Flask server is running!'

# Initialize and run the bot
# Commented out to isolate the Flask app
# updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
# updater.dispatcher.add_handler(CommandHandler('start', start))
# updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
# updater.start_polling()
# updater.idle()
