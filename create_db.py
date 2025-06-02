from app import create_app, db
from app.models.user import User
from app.models.phrase import Phrase
from app.models.quiz import QuizResult

app = create_app()

with app.app_context():
    # データベースを作成
    db.create_all()
    print("データベースを作成しました") 