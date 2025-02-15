from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from database import db
from models import Player, GameNight, GameNightPlayers, Round, Score  # ✅ הייבוא החסר

app = Flask(__name__)
CORS(app)

# הגדרת החיבור למסד הנתונים (Neon PostgreSQL בענן)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_MYB6cwgpKe1m@ep-rapid-water-a86hzhzs-pooler.eastus2.azure.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/players', methods=['POST'])
def add_player():
    data = request.json
    new_player = Player(name=data['name'])
    db.session.add(new_player)
    db.session.commit()
    return jsonify({"message": "Player added"}), 201

@app.route('/players', methods=['GET'])
def get_players():
    players = Player.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in players])


# **יצירת ערב משחק**
@app.route('/game_night', methods=['POST'])
def start_game_night():
    data = request.json
    new_game_night = GameNight(host_id=data['host_id'])
    db.session.add(new_game_night)
    db.session.commit()
    return jsonify({"game_night_id": new_game_night.id}), 201


# **בחירת המשתתפים לערב משחק**
@app.route('/game_night/select_players', methods=['POST'])
def select_players():
    data = request.json
    game_night_id = data['game_night_id']
    players = data['players']

    for player_id in players:
        new_entry = GameNightPlayers(game_night_id=game_night_id, player_id=player_id)
        db.session.add(new_entry)

    db.session.commit()
    return jsonify({"message": "Players selected for game night"}), 201


# **הוספת סיבוב והזנת תוצאות**
@app.route('/round/submit_scores', methods=['POST'])
def submit_scores():
    data = request.json
    round_id = data['round_id']
    scores = data['scores']

    loser = None
    for player_id, score in scores.items():
        new_score = Score(round_id=round_id, player_id=player_id, score=score)
        db.session.add(new_score)

        if score >= 5:
            loser = player_id

    db.session.commit()

    return jsonify({"message": "Scores submitted", "loser": loser}), 201


# **קביעת המפסיד של הערב**
@app.route('/game_night/loser/<int:game_night_id>', methods=['GET'])
def get_game_night_loser(game_night_id):
    query = """
    SELECT p.name, COUNT(s.id) AS losses
    FROM Players p
    JOIN Scores s ON p.id = s.player_id
    JOIN Rounds r ON s.round_id = r.id
    WHERE r.game_night_id = :game_night_id AND s.score >= 5
    GROUP BY p.name
    ORDER BY losses DESC
    LIMIT 1;
    """
    result = db.session.execute(query, {"game_night_id": game_night_id}).fetchone()
    if result:
        return jsonify({"loser": result[0], "losses": result[1]})
    return jsonify({"message": "No data"}), 404


if __name__ == '__main__':
    app.run(debug=True)
