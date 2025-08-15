from typing import Optional
from app.model.word import Word, WordRepository


class WordsInMemoryRepository(WordRepository):

    def __init__(self):
        self.words = []

    def get_word(self, word_id: str) -> Optional[Word]:
        for w in self.words:
            if w.id == word_id:
                return w
        return None

    def save(self, word: Word):
        self.words.append(word)
        return word
