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
        return jsonify(new_player.to_dict()), 200  # Return a 200 Created status
    except Exception as e:
        # If an error occurs while saving to the database, return an error response
        db.session.rollback()  # Rollback the session in case of an error
        return jsonify({"error": "Failed to create player", "details": str(e)}), 500


@routes.route('/players', methods=['GET'])
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
    
    
@routes.route('/teams/<string:id>', methods=['GET'])
def get_team_by_id(id):
    try:
        # Query the database for the player by ID
        team = Team.query.get(id)

        # If player does not exist, return a 404 error
        if team is None:
            return jsonify({"error": "Team not found"}), 404

        # Return the team data as JSON
        return jsonify(team.to_dict()), 200
    
    except Exception as e:
        # If there's an error, return an internal server error
        return jsonify({"error": "Failed to retrieve team", "details": str(e)}), 500
    
    
@routes.route('/teams', methods=['POST'])
def create_team():
    data = request.get_json()

    team_name = data.get('teamName')
    player_ids = data.get('players')

    # Validate that the team name is provided
    if not team_name:
        return jsonify({"error": "Team name is required."}), 400

    # Check if the team already exists
    existing_team = Team.query.filter_by(teamName=team_name).first()
    if existing_team:
        return jsonify({"error": "Team name already exists"}), 400

    # Ensure that exactly 5 players are provided
    if not player_ids or len(player_ids) != 5:
        return jsonify({"error": "A team must have exactly 5 players."}), 400

    # Ensure players are unique (no duplicates)
    if len(player_ids) != len(set(player_ids)):
        return jsonify({"error": "Players must be unique."}), 400

    # Check if all players exist and are not already in another team
    existing_players = Player.query.filter(Player.id.in_(player_ids)).all()
    if len(existing_players) != 5:
        return jsonify({"error": "One or more players do not exist."}), 400

    for player in existing_players:
        if player.team:  # Assuming `team` is the relationship attribute
            return jsonify({"error": f"Player {player.id} is already in another team."}), 400

    # Create a new team
    new_team = Team(teamName=team_name)

    try:
        # Add the team to the session
        db.session.add(new_team)
        db.session.flush()  # Flush to generate `new_team.id` before assigning players

        # Assign the team to the players
        for player in existing_players:
            player.team = new_team  # Link the player to the team

        # Commit to save the new team and updated players
        db.session.commit()

        # Prepare the response data
        team_data = new_team.to_dict()
        team_data['players'] = [player.to_dict() for player in existing_players]

        # Return the created team information
        return jsonify(team_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create team", "details": str(e)}), 500


@routes.route('/matches', methods=['POST'])
def process_match():
    def calculate_K(time):
        if time < 500:
            return 50
        if time < 1000:
            return 40
        if time < 3000:
            return 30
        if time < 5000:
            return 20
        return 10

    data = request.get_json()

    # Extract parameters
    team1_id = data.get('team1Id')
    team2_id = data.get('team2Id')
    winning_team_id = data.get('winningTeamId', None)
    duration = data.get('duration')

    # Validate input
    if not team1_id or not team2_id or duration is None:
        return jsonify({"error": "Missing required fields"}), 400

    if not isinstance(duration, int) or duration <= 0:
        return jsonify({"error": "Duration must be a positive integer"}), 400

    if team1_id == team2_id:
        return jsonify({"error": "The two team IDs cannot be the same"}), 400

    # Fetch teams from the database
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)

    if not team1 or not team2:
        return jsonify({"error": "One or both teams do not exist"}), 400

    if winning_team_id and winning_team_id not in {team1_id, team2_id}:
        return jsonify({"error": "Winning team ID does not match either team"}), 400

    try:
        outcome = "X"

        # Fetch players as lists
        team1_players = team1.players.all()
        team2_players = team2.players.all()

        # Calculate average Elo
        team1_average_elo = sum(player.elo for player in team1_players) / len(team1_players)
        team2_average_elo = sum(player.elo for player in team2_players) / len(team2_players)

        # Add the duration to all players' hoursPlayed
        for player in team1_players + team2_players:
            player.hoursPlayed += duration

        # Update stats for the winning and losing teams
        if winning_team_id:
            if winning_team_id == team1_id:
                outcome = '1'
                for player in team1_players:
                    player.wins += 1
                for player in team2_players:
                    player.losses += 1
            elif winning_team_id == team2_id:
                outcome = '2'
                for player in team2_players:
                    player.wins += 1
                for player in team1_players:
                    player.losses += 1

        # Update Elo ratings
        for player in team1_players:
            E = 1 / (1 + 10**((team2_average_elo - player.elo) / 400))
            adjustment = 0.5 if outcome == "X" else (1 if outcome == "1" else 0)
            player.elo += calculate_K(player.hoursPlayed) * (adjustment - E)

        for player in team2_players:
            E = 1 / (1 + 10**((team1_average_elo - player.elo) / 400))
            adjustment = 0.5 if outcome == "X" else (1 if outcome == "2" else 0)
            player.elo += calculate_K(player.hoursPlayed) * (adjustment - E)

        # Commit the changes to the database
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update player stats", "details": str(e)}), 500

    # Return a success response
    return jsonify({"message": "Match processed successfully"}), 200