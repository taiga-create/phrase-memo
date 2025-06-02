import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # セキュリティ設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///memo.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') 