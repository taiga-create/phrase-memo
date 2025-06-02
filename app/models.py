from . import db

class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phrase = db.Column(db.String(200), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)
    example = db.Column(db.String(300))
    example_meaning = db.Column(db.String(300))
