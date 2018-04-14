from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import models
import os

app = Flask(__name__)
dburi = os.environ['dbhost']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{usr}:{dbpass}@{host}:5432/{db}'.format(
    usr=os.environ['dbuser'],
    dbpass=os.environ['dbpass'],
    host=os.environ['dbhost'],
    db=os.environ['dbname']
)
models.db.init_app(app)
with app.app_context():
    models.db.create_all()
api = Api(app, prefix='/api')
auth = HTTPBasicAuth()
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits['40 per minute', '1 per second'],
)

puzzleSerializer = models.PuzzleSerializer()

class Puzzle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('fen', type=str, required=True)
    parser.add_argument('url', type=str, required=False)
    parser.add_argument('solution', type=str, required=False)

    def get(self, puzzle_id):
        queried_data = models.Puzzle.query.get(puzzle_id)
        result = puzzleSerializer.dump(queried_data)
        return result
    
    def post(self):
        data = Puzzle.parser.parse_args()
        new_puzzle = models.Puzzle(fen=data['fen'], game_url=data['url'], solution=data['solution'])
        models.db.session.add(new_puzzle)
        models.db.session.commit()
        return data, 201

api.add_resource(Puzzle, '/puzzle' , '/puzzle/<int:puzzle_id>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
