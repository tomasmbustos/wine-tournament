import json
import os
from typing import List, Optional, Dict
from app.model.wine_tournament import TournamentRepository, Participant, Vote


class TournamentJsonRepository(TournamentRepository):
    def __init__(self, participants_file: str = "data/participants.json", votes_file: str = "data/votes.json"):
        self.participants_file = participants_file
        self.votes_file = votes_file
        self._ensure_data_directory()
        self._ensure_files_exist()

    def _ensure_data_directory(self):
        os.makedirs("data", exist_ok=True)

    def _ensure_files_exist(self):
        if not os.path.exists(self.participants_file):
            with open(self.participants_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.votes_file):
            with open(self.votes_file, 'w') as f:
                json.dump([], f)

    def save_participant(self, participant: Participant) -> None:
        participants = self._load_participants_from_file()
        
        # Remove existing participant with same id if exists
        participants = [p for p in participants if p.get("id") != participant.id]
        
        # Add new participant
        participants.append(participant.dict(by_alias=True))
        
        with open(self.participants_file, 'w') as f:
            json.dump(participants, f, indent=2)

    def get_all_participants(self) -> List[Participant]:
        participants_data = self._load_participants_from_file()
        return [Participant(**p) for p in participants_data]

    def get_participant(self, participant_id: str) -> Optional[Participant]:
        participants = self.get_all_participants()
        for participant in participants:
            if participant.id == participant_id:
                return participant
        return None

    def save_vote(self, vote: Vote) -> None:
        votes = self._load_votes_from_file()
        
        # Remove existing vote from same participant if exists
        votes = [v for v in votes if v.get("participantId") != vote.participant_id]
        
        # Add new vote
        votes.append(vote.dict(by_alias=True))
        
        with open(self.votes_file, 'w') as f:
            json.dump(votes, f, indent=2)

    def get_all_votes(self) -> List[Vote]:
        votes_data = self._load_votes_from_file()
        return [Vote(**v) for v in votes_data]

    def get_wine_counts(self) -> Dict[int, int]:
        participants = self.get_all_participants()
        wine_counts = {}
        
        for participant in participants:
            for wine_id in participant.assigned_wines:
                wine_counts[wine_id] = wine_counts.get(wine_id, 0) + 1
        
        return wine_counts

    def _load_participants_from_file(self) -> List[dict]:
        try:
            with open(self.participants_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _load_votes_from_file(self) -> List[dict]:
        try:
            with open(self.votes_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []