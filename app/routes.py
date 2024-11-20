# app/routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models import Player
from app.models import Team

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return "Hello, Flask!"

@routes.route('/players/create', methods=['POST'])
def receive_data():
    # Get the JSON data from the request
    data = request.get_json()

    # Check if 'nickname' is in the data
    nickname = data.get('nickname')

    if not nickname:
        # If no nickname is provided, return an error response with a 400 Bad Request status
        return jsonify({"error": "Nickname is required"}), 400
    
    # Check if a player with the same nickname already exists in the database
    existing_player = Player.query.filter_by(nickname=nickname).first()
    
    if existing_player:
        # If player with the same nickname exists, return a 400 error response
        return jsonify({"error": "Player with this nickname already exists"}), 400
    
    # Create a new Player object
    new_player = Player(
        nickname=nickname
    )

    try:
        # Add the player to the database
        db.session.add(new_player)
        db.session.commit()  # Commit the transaction to save the player to the database

        # Return a success response with the player data
        return jsonify(new_player.to_dict()), 201  # Return a 201 Created status
    except Exception as e:
        # If an error occurs while saving to the database, return an error response
        db.session.rollback()  # Rollback the session in case of an error
        return jsonify({"error": "Failed to create player", "details": str(e)}), 500


@routes.route('/players/getall', methods=['GET'])
def get_all_players():
    try:
        # Query all players from the database
        players = Player.query.all()

        # If no players found, return an empty list
        if not players:
            return jsonify([]), 200

        # Convert each player object to a dictionary
        players_list = [player.to_dict() for player in players]

        # Return the list of players as a JSON response
        return jsonify(players_list), 200
    except Exception as e:
        # If there's an error, return an error message
        return jsonify({"error": "Failed to retrieve players", "details": str(e)}), 500
    
@routes.route('/players/<string:id>', methods=['GET'])
def get_player_by_id(id):
    try:
        # Query the database for the player by ID
        player = Player.query.get(id)

        # If player does not exist, return a 404 error
        if player is None:
            return jsonify({"error": "Player not found"}), 404

        # Return the player data as JSON
        return jsonify(player.to_dict()), 200
    except Exception as e:
        # If there's an error, return an internal server error
        return jsonify({"error": "Failed to retrieve player", "details": str(e)}), 500
    
    
@routes.route('/teams/create', methods=['POST'])
def create_team():
    data = request.get_json()

    team_name = data.get('teamName')
    player_ids = data.get('players')
    
    # Check if the team already exists
    existing_team = Team.query.filter_by(teamName=team_name).first()
    if existing_team:
        return jsonify({"error": "Team name already exists"}), 400
    
    # Ensure that exactly 5 players are provided
    if len(player_ids) != 5:
        return jsonify({"error": "A team must have exactly 5 players."}), 400

    # Ensure players are unique (no duplicates)
    if len(player_ids) != len(set(player_ids)):
        return jsonify({"error": "Players must be unique."}), 400
    
    # Check if any of the players are already in another team
    existing_players = Player.query.filter(Player.id.in_(player_ids)).all()
    # Check if we have all 5 players
    if len(existing_players) != 5:
        return jsonify({"error": f"One or more players do not exist."}), 400
    for player in existing_players:
        if player.team_id:
            return jsonify({"error": f"Player {player.nickname} is already in another team."}), 400

    # Create a new team
    new_team = Team(teamName=team_name)
    
    # Add the players to the team and update their `team_id`
    for player_id in player_ids:
        player = Player.query.get(player_id)
        if player:
            player.team_id = new_team.id  # Assign team_id to the player
            new_team.players.append(player)  # Add player to the team's players list

    try:
        # Commit to save the new team and players
        db.session.add(new_team)
        db.session.commit()

        team_data = new_team.to_dict()  # Convert team to dict
        team_data['players'] = [player.to_dict() for player in existing_players]  # Add detailed player data to the team
        # Return the created team information
        return jsonify(team_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create team", "details": str(e)}), 500