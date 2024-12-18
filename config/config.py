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
    LABEL_STUDIO_DB_HOSTNAME = os.getenv('LABEL_STUDIO_DB_HOSTNAME')
    LABEL_STUDIO_DB_PORT = os.getenv('LABEL_STUDIO_DB_PORT')
    LABEL_STUDIO_DB_NAME = os.getenv('LABEL_STUDIO_DB_NAME')
    LABEL_STUDIO_DB_USERNAME = os.getenv('LABEL_STUDIO_DB_USERNAME')
    LABEL_STUDIO_DB_PASSWORD = os.getenv('LABEL_STUDIO_DB_PASSWORD')