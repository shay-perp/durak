from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# חיבור למסד נתונים (שנה לפי ה-PostgreSQL שלך)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db.supabase.co:5432/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# **טבלת שחקנים**
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# **טבלת ערבי משחק**
class GameNight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    host_id = db.Column(db.Integer, db.ForeignKey('player.id'))

# **טבלת סיבובים**
class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_night_id = db.Column(db.Integer, db.ForeignKey('game_night.id'))
    name = db.Column(db.String(100))
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# **טבלת תוצאות**
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    score = db.Column(db.Integer, nullable=False)

# יצירת מסד נתונים
with app.app_context():
    db.create_all()

# **API - רישום שחקן חדש**
@app.route('/players', methods=['POST'])
def add_player():
    data = request.json
    new_player = Player(name=data['name'])
    db.session.add(new_player)
    db.session.commit()
    return jsonify({"message": "Player added"}), 201

# **API - קבלת רשימת שחקנים**
@app.route('/players', methods=['GET'])
def get_players():
    players = Player.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in players])

# **API - יצירת ערב משחק**
@app.route('/game_night', methods=['POST'])
def start_game_night():
    data = request.json
    new_game_night = GameNight(host_id=data['host_id'])
    db.session.add(new_game_night)
    db.session.commit()
    return jsonify({"game_night_id": new_game_night.id}), 201

# **API - הוספת סיבוב**
@app.route('/round', methods=['POST'])
def add_round():
    data = request.json
    new_round = Round(game_night_id=data['game_night_id'], name=data['name'], winner_id=data['winner_id'])
    db.session.add(new_round)
    db.session.commit()
    return jsonify({"round_id": new_round.id}), 201

# **API - הוספת תוצאה**
@app.route('/score', methods=['POST'])
def add_score():
    data = request.json
    new_score = Score(round_id=data['round_id'], player_id=data['player_id'], score=data['score'])
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"message": "Score recorded"}), 201

# **API - סטטיסטיקות הפסדים**
@app.route('/stats', methods=['GET'])
def get_stats():
    query = """
    SELECT p.name, COUNT(s.id) AS losses
    FROM Players p
    JOIN Scores s ON p.id = s.player_id
    WHERE s.score < 5
    GROUP BY p.name
    ORDER BY losses DESC;
    """
    result = db.session.execute(query).fetchall()
    stats = [{"name": row[0], "losses": row[1]} for row in result]
    return jsonify(stats)

# **הרצת השרת**
if __name__ == '__main__':
    app.run(debug=True)
