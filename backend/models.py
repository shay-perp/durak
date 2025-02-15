from database import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class GameNight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, server_default=db.func.now())
    host_id = db.Column(db.Integer, db.ForeignKey('player.id'))

class GameNightPlayers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_night_id = db.Column(db.Integer, db.ForeignKey('game_night.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_night_id = db.Column(db.Integer, db.ForeignKey('game_night.id'))
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    score = db.Column(db.Integer, nullable=False)
