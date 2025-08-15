import abc
from typing import Optional
from pydantic import BaseModel, Field


class Word(BaseModel):
    id: str = Field(alias="id")
    word: str = Field(alias="word")
    transformed_word: Optional[str] = Field(alias="reverseWord", default=None)
    from_ip: Optional[str] = Field(alias="fromIp", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class WordRepository(abc.ABC):

    @abc.abstractmethod
    def save(self, word: Word):
        pass

    @abc.abstractmethod
    def get_word(self, word_id: str) -> Optional[Word]:
        pass
