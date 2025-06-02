from datetime import datetime
from app import db

class Phrase(db.Model):
    __tablename__ = 'phrases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    english = db.Column(db.String(500), nullable=False)
    japanese = db.Column(db.String(500), nullable=False)
    example = db.Column(db.String(1000))
    note = db.Column(db.String(1000))
    is_memorized = db.Column(db.Boolean, default=False)
    last_reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Phrase {self.english}>'
    
    def update_memorization_status(self, is_memorized):
        self.is_memorized = is_memorized
        self.last_reviewed_at = datetime.utcnow() 