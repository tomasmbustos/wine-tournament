import pytest
import inject
from decouple import config
from app.usecase.word_transformer import WordTransformerUCImpl
from app.model.word import WordRepository
from app.gateway.my_ip import MyIP, MyIPImpl
from app.repository.words_in_memory import WordsInMemoryRepository


def my_config(binder):
    binder.bind(WordRepository, WordsInMemoryRepository())
    binder.bind(MyIP, MyIPImpl())

@pytest.fixture
def inject_config():
    inject.clear_and_configure(my_config)

@pytest.mark.skipif(not config("LIVE_TESTS", default=False, cast=bool), reason="Integration tests are disabled")
@pytest.mark.asyncio
async def test_reverse_and_concat():
    my_ip = MyIPImpl()

    word_repo = WordsInMemoryRepository()
    word_transformer = WordTransformerUCImpl(concat_with=" test")
    word_transformer.word_repo = word_repo
    word_transformer.ip_gw = my_ip

    result = await word_transformer.reverse_and_concat(new_word="a si siht")
    assert result == { 
        "id": result["id"], # This will be a random UUID
        "word": "a si siht", 
        "reverseWord": "this is a test",
        "fromIp": result["fromIp"] # This will be the IP of the machine running the test
    }
