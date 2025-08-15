import abc
import uuid

import inject
from app.model.word import WordRepository, Word
from app.gateway.my_ip import MyIP


class WordTransformerUC(abc.ABC):
    @abc.abstractmethod
    async def reverse_and_concat(self, new_word: str) -> dict:
        pass


class WordTransformerUCImpl(WordTransformerUC):
    word_repo: WordRepository = inject.attr(WordRepository)
    ip_gw: MyIP = inject.attr(MyIP)

    def __init__(self, concat_with: str):
        self.concat_with = concat_with

    async def reverse_and_concat(self, new_word: str) -> dict:
        reversed_and_concat = new_word[::-1] + self.concat_with
        my_ip = await self.ip_gw.get_ip()
        word = Word(
            id=str(uuid.uuid4()),
            word=new_word,
            transformed_word=reversed_and_concat,
            from_ip=my_ip
        )
        self.word_repo.save(word)
        return word.dict(by_alias=True)
