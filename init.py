from flask import Flask
from flask import request, jsonify
# from flask_bcrypt import Bcrypt
# from flask_session import Session
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv
import secrets
import ssl
import smtplib
from email.message import EmailMessage
from supabase import create_client, Client


load_dotenv()

app = Flask(__name__)

# redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

otp_dict = {}
email_sender = os.getenv('EMAIL_SENDER')
email_password = os.getenv('EMAIL_PASSWORD')


url=os.getenv('DTB_URL')
key=os.getenv('DTB_KEY')
supabase: Client = create_client(url, key)

# require origin
ALLOW_ORIGINS = ["http://localhost:5173","http://localhost:5000","https://weather-app-client-b5gf.onrender.com", "https://weather-app-server-pqw9.onrender.com"]
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5173","http://localhost:5000","https://weather-app-client-b5gf.onrender.com", "https://weather-app-server-pqw9.onrender.com"]
    }
})