from fastapi import APIRouter
from app.api.word_transformer import word_transformer_router
from app.api.wine_tournament import wine_tournament_router
app_router = APIRouter()

app_router.include_router(word_transformer_router, prefix="/words", tags=["Words"])
app_router.include_router(wine_tournament_router, prefix="/tournament", tags=["Wine Tournament"])
