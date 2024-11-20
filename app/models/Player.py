# app/models.py
from app import db
import uuid

class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Auto-generate UUID
    nickname = db.Column(db.String(100), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    elo = db.Column(db.Integer, default=0)
    hoursPlayed = db.Column(db.Integer, default=0)
    team_id = db.Column(db.String(36), db.ForeignKey('team.id'), nullable=True)  # ForeignKey to Team (use team_id for clarity)
    ratingAdjustment = db.Column(db.Integer, nullable=True)

    # Relationship to Team (this creates a back-reference to the Team object in Player)
    team = db.relationship('Team', back_populates='players', lazy='joined')  # Reference to Team object

    def to_dict(self):
        """Convert the Player object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "nickname": self.nickname,
            "wins": self.wins,
            "losses": self.losses,
            "elo": self.elo,
            "hoursPlayed": self.hoursPlayed,
            "team": self.team.teamName if self.team else None,  # Add team name to the response
            "ratingAdjustment": self.ratingAdjustment,
        }
