# app/models.py
from app import db
import uuid

class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Auto-generate UUID
    teamName = db.Column(db.String(100), unique=True, nullable=False)
    
    players = db.relationship('Player', back_populates='team', lazy='dynamic')  # Relationship to Player

    def to_dict(self):
        """Convert the Team object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "teamName": self.teamName,
            "players": [player.to_dict() for player in self.players],
        }
