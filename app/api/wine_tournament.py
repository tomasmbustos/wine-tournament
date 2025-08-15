from fastapi import APIRouter, HTTPException, Query
from typing import List
import inject
from app.usecase.wine_tournament import WineTournamentUC
from app.model.wine_tournament import (
    CreateParticipantRequest,
    CreateParticipantResponse,
    Participant,
    Vote,
    WineScore
)

wine_tournament_router = APIRouter()


@wine_tournament_router.post("/participants/suggest", response_model=CreateParticipantResponse)
async def suggest_participant_wines(
    request: CreateParticipantRequest,
    total_wines: int = Query(default=20, description="Total number of wines in the tournament")
):
    tournament_uc: WineTournamentUC = inject.instance(WineTournamentUC)
    try:
        response = await tournament_uc.create_participant(request, total_wines)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wine_tournament_router.post("/participants/confirm", response_model=dict)
async def confirm_participant(participant: Participant):
    tournament_uc: WineTournamentUC = inject.instance(WineTournamentUC)
    try:
        success = await tournament_uc.confirm_participant(participant)
        if success:
            return {"success": True, "message": "Participant created successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid wine assignment - some wines exceed maximum participants")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wine_tournament_router.get("/participants", response_model=List[Participant])
async def get_all_participants():
    tournament_uc: WineTournamentUC = inject.instance(WineTournamentUC)
    try:
        participants = await tournament_uc.get_all_participants()
        return participants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wine_tournament_router.post("/votes", response_model=dict)
async def submit_vote(vote: Vote):
    tournament_uc: WineTournamentUC = inject.instance(WineTournamentUC)
    try:
        success = await tournament_uc.submit_vote(vote)
        if success:
            return {"success": True, "message": "Vote submitted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid vote - check participant ID and wine assignments")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wine_tournament_router.get("/leaderboard", response_model=List[WineScore])
async def get_leaderboard():
    tournament_uc: WineTournamentUC = inject.instance(WineTournamentUC)
    try:
        leaderboard = await tournament_uc.get_leaderboard()
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wine_tournament_router.get("/voting-stats", response_model=dict)
async def get_voting_stats():
    tournament_uc: WineTournamentUC = inject.instance(WineTournamentUC)
    try:
        votes = tournament_uc.tournament_repo.get_all_votes()
        participants = await tournament_uc.get_all_participants()
        
        # Get unique participant IDs who have voted
        voted_participant_ids = set(vote.participant_id for vote in votes)
        
        total_votes = len(votes)
        total_participants = len(participants)
        voting_percentage = (total_votes / total_participants * 100) if total_participants > 0 else 0
        
        # Create participant status list
        participant_status = []
        for participant in participants:
            participant_status.append({
                "id": participant.id,
                "name": participant.name,
                "has_voted": participant.id in voted_participant_ids
            })
        
        return {
            "total_votes": total_votes,
            "total_participants": total_participants,
            "voting_percentage": round(voting_percentage, 1),
            "participant_status": participant_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))