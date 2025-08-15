import abc
import uuid
import random
from typing import List, Dict
import inject
from app.model.wine_tournament import (
    TournamentRepository, 
    Participant, 
    Vote, 
    WineScore, 
    CreateParticipantRequest,
    CreateParticipantResponse
)


class WineTournamentUC(abc.ABC):
    @abc.abstractmethod
    async def create_participant(self, request: CreateParticipantRequest, total_wines: int) -> CreateParticipantResponse:
        pass

    @abc.abstractmethod
    async def get_all_participants(self) -> List[Participant]:
        pass

    @abc.abstractmethod
    async def submit_vote(self, vote: Vote) -> bool:
        pass

    @abc.abstractmethod
    async def get_leaderboard(self) -> List[WineScore]:
        pass

    @abc.abstractmethod
    async def validate_wine_assignment(self, wine_ids: List[int]) -> bool:
        pass


class WineTournamentUCImpl(WineTournamentUC):
    tournament_repo: TournamentRepository = inject.attr(TournamentRepository)

    def __init__(self, max_participants_per_wine: int = 5):
        self.max_participants_per_wine = max_participants_per_wine

    async def create_participant(self, request: CreateParticipantRequest, total_wines: int) -> CreateParticipantResponse:
        participant_id = str(uuid.uuid4())
        
        # If wines not provided, generate random suggestions
        if not request.assigned_wines:
            suggested_wines = await self._generate_wine_suggestions(total_wines)
        else:
            suggested_wines = request.assigned_wines
            # Validate the wine assignment
            is_valid = await self.validate_wine_assignment(suggested_wines)
            if not is_valid:
                # If invalid, generate new suggestions
                suggested_wines = await self._generate_wine_suggestions(total_wines)
        
        # Always validate the final suggestions before returning
        is_valid = await self.validate_wine_assignment(suggested_wines)
        if not is_valid:
            # If even generated suggestions are invalid, try one more time
            suggested_wines = await self._generate_wine_suggestions(total_wines)

        participant = Participant(
            id=participant_id,
            name=request.name,
            assigned_wines=suggested_wines
        )

        return CreateParticipantResponse(
            participant=participant,
            suggested_wines=suggested_wines
        )

    async def confirm_participant(self, participant: Participant) -> bool:
        # Final validation before saving (exclude current participant from wine counts)
        is_valid = await self.validate_wine_assignment_for_participant(participant.assigned_wines, participant.id)
        if is_valid:
            self.tournament_repo.save_participant(participant)
            return True
        return False

    async def get_all_participants(self) -> List[Participant]:
        return self.tournament_repo.get_all_participants()

    async def submit_vote(self, vote: Vote) -> bool:
        # Validate that participant exists
        participant = self.tournament_repo.get_participant(vote.participant_id)
        if not participant:
            return False

        # Validate that all voted wines are assigned to the participant
        voted_wines = {vote.first_place, vote.second_place, vote.third_place}
        if not voted_wines.issubset(set(participant.assigned_wines)):
            return False

        # Validate that all positions are different wines
        if len(voted_wines) != 3:
            return False
        
        # Handle case where participant has fewer than 5 wines (when tournament is nearly full)
        if len(participant.assigned_wines) < 5:
            # Allow voting with fewer wines, but all 3 votes must still be for different wines
            pass

        self.tournament_repo.save_vote(vote)
        return True

    async def get_leaderboard(self) -> List[WineScore]:
        votes = self.tournament_repo.get_all_votes()
        wine_scores = {}

        for vote in votes:
            # First place: 3 points
            wine_scores[vote.first_place] = wine_scores.get(vote.first_place, 0) + 3
            # Second place: 2 points
            wine_scores[vote.second_place] = wine_scores.get(vote.second_place, 0) + 2
            # Third place: 1 point
            wine_scores[vote.third_place] = wine_scores.get(vote.third_place, 0) + 1

        # Convert to list of WineScore objects and sort by points descending
        leaderboard = [
            WineScore(wine_id=wine_id, total_points=points)
            for wine_id, points in wine_scores.items()
        ]
        
        return sorted(leaderboard, key=lambda x: x.total_points, reverse=True)

    async def validate_wine_assignment(self, wine_ids: List[int]) -> bool:
        # Allow fewer than 5 wines when tournament is nearly full
        if len(wine_ids) < 1 or len(wine_ids) > 5:
            return False

        # Check for duplicate wine IDs
        if len(wine_ids) != len(set(wine_ids)):
            return False

        wine_counts = self.tournament_repo.get_wine_counts()
        
        for wine_id in wine_ids:
            current_count = wine_counts.get(wine_id, 0)
            if current_count >= self.max_participants_per_wine:
                return False

        return True

    async def validate_wine_assignment_for_participant(self, wine_ids: List[int], participant_id: str) -> bool:
        # Allow fewer than 5 wines when tournament is nearly full
        if len(wine_ids) < 1 or len(wine_ids) > 5:
            return False

        # Check for duplicate wine IDs
        if len(wine_ids) != len(set(wine_ids)):
            return False

        # Get current wine counts excluding this participant
        all_participants = self.tournament_repo.get_all_participants()
        wine_counts = {}
        
        for participant in all_participants:
            # Skip the current participant to exclude their previous assignment
            if participant.id == participant_id:
                continue
                
            for wine_id in participant.assigned_wines:
                wine_counts[wine_id] = wine_counts.get(wine_id, 0) + 1
        
        # Now validate the new assignment
        for wine_id in wine_ids:
            current_count = wine_counts.get(wine_id, 0)
            if current_count >= self.max_participants_per_wine:
                return False

        return True

    async def _generate_wine_suggestions(self, total_wines: int) -> List[int]:
        wine_counts = self.tournament_repo.get_wine_counts()
        
        # Get available wines (those with less than max participants)
        available_wines = [
            wine_id for wine_id in range(1, total_wines + 1)
            if wine_counts.get(wine_id, 0) < self.max_participants_per_wine
        ]
        
        # If we have enough available wines, great! If not, we'll use what we have
        # and the validation will handle any edge cases
        
        if len(available_wines) >= 5:
            # Normal case: randomly select 5 from available wines
            return random.sample(available_wines, 5)
        elif len(available_wines) > 0:
            # Tournament nearly full: use all available wines
            # This gives participants the best possible wine selection
            return available_wines
        else:
            # Tournament completely full: return empty list 
            # This will trigger appropriate error handling upstream
            return []