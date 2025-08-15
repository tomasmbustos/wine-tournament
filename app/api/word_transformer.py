import inject
from typing import Optional
from app.api.auth import validate_apikey_request
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.usecase.word_transformer import WordTransformerUC

word_transformer_router = APIRouter()


class WordTransformRequest(BaseModel):
    word: str


@word_transformer_router.post("/transform")
async def handler(
        word_transform_request: WordTransformRequest,
        _=Depends(validate_apikey_request)
):
    uc:WordTransformerUC = inject.instance(WordTransformerUC)
    new_word = await uc.reverse_and_concat(word_transform_request.word)
    return new_word
