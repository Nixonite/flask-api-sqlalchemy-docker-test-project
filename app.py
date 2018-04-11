from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
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
api = Api(app)

class Puzzle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('fen', type=str, required=True)
    parser.add_argument('url', type=str, required=False)
    parser.add_argument('solution', type=str, required=False)

    def get(self, puzzle_id):
        queried_data = models.Puzzle.query.get(puzzle_id)
        return {puzzle_id: queried_data.fen}
    def post(self):
        data = Puzzle.parser.parse_args()
        new_puzzle = models.Puzzle(fen=data['fen'], game_url=data['url'], solution=data['solution'])
        models.db.session.add(new_puzzle)
        models.db.session.commit()
        return data, 201

api.add_resource(Puzzle, '/<int:puzzle_id>')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
