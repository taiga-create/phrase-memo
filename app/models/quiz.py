from datetime import datetime
from app import db

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    quiz_type = db.Column(db.String(20), nullable=False)  # 'translation', 'listening', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def accuracy_percentage(self):
        return round((self.score / self.total_questions) * 100, 1) if self.total_questions > 0 else 0 