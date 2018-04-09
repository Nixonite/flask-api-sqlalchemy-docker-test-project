from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Puzzle(Base):
    id = db.Column(db.Integer, primary_key = True)
    game_url = db.Column(db.String(200), unique=True, nullable=True)
    fen = db.Column(db.String(100), unique=True, nullable=False)
    solution = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return "<Puzzle {}>".format(self.fen)