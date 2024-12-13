import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    DEBUG = os.getenv('DEBUG') == 'True'
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL')
    LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY')