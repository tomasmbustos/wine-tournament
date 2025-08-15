from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import abc


class Participant(BaseModel):
    id: str = Field(alias="id")
    name: str = Field(alias="name")
    assigned_wines: List[int] = Field(alias="assignedWines")

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class Vote(BaseModel):
    participant_id: str = Field(alias="participantId")
    first_place: int = Field(alias="firstPlace")  # 3 points
    second_place: int = Field(alias="secondPlace")  # 2 points
    third_place: int = Field(alias="thirdPlace")  # 1 point

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class WineScore(BaseModel):
    wine_id: int = Field(alias="wineId")
    total_points: int = Field(alias="totalPoints")

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class CreateParticipantRequest(BaseModel):
    name: str
    assigned_wines: Optional[List[int]] = None


class CreateParticipantResponse(BaseModel):
    participant: Participant
    suggested_wines: List[int] = Field(alias="suggestedWines")

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class TournamentRepository(abc.ABC):
    @abc.abstractmethod
    def save_participant(self, participant: Participant) -> None:
        pass

    @abc.abstractmethod
    def get_all_participants(self) -> List[Participant]:
        pass

    @abc.abstractmethod
    def get_participant(self, participant_id: str) -> Optional[Participant]:
        pass

    @abc.abstractmethod
    def save_vote(self, vote: Vote) -> None:
        pass

    @abc.abstractmethod
    def get_all_votes(self) -> List[Vote]:
        pass

    @abc.abstractmethod
    def get_wine_counts(self) -> Dict[int, int]:
        pass