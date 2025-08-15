from decouple import config
from pydantic import BaseModel
from typing import Optional
from loggers_conf.gcp import configure_logger as gcp_configure_logger
from utils.secret_manager import set_env_vars_from_gcp_secret_manager
from loguru import logger

from app.gateway.my_ip import MyIP, MyIPImpl

from app.model.word import WordRepository
from app.repository.words_in_memory import WordsInMemoryRepository

from app.usecase.word_transformer import WordTransformerUC, WordTransformerUCImpl

from app.model.wine_tournament import TournamentRepository
from app.repository.tournament_json import TournamentJsonRepository
from app.usecase.wine_tournament import WineTournamentUC, WineTournamentUCImpl


class Configuration(BaseModel):
    ENVIRONMENT: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None
    GCP_SECRET_NAME: Optional[str] = None
    GCP_SECRET_VERSION: Optional[str] = None


def manage_configuration_secrets(configuration: Configuration):
    if config("LOCAL_ENV", default=False, cast=bool) is True:
        logger.info("Local Configuration. Loading from .env file")
        # When using Google Services
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(config("PROJECT_ROOT"),
        #                                                             "credentials/service_account.json")
    else:
        gcp_configure_logger()
        set_env_vars_from_gcp_secret_manager(
            configuration.GCP_PROJECT_ID,
            configuration.GCP_SECRET_NAME,
            configuration.GCP_SECRET_VERSION
        )


def new_configuration():
    configuration = Configuration(ENVIRONMENT=config("ENVIRONMENT"))
    configuration.GCP_PROJECT_ID = config("GCP_PROJECT_ID", None)
    configuration.GCP_SECRET_NAME = config("GCP_SECRET_NAME", None)
    configuration.GCP_SECRET_VERSION = config("GCP_SECRET_VERSION", None)
    # Manage secrets
    manage_configuration_secrets(configuration)
    return configuration


def di_configuration(binder, _=new_configuration()):
    # Repositories
    binder.bind(WordRepository, WordsInMemoryRepository())
    binder.bind(TournamentRepository, TournamentJsonRepository())
    # Gateways
    binder.bind(MyIP, MyIPImpl())
    # Usecases
    binder.bind(WordTransformerUC, WordTransformerUCImpl(
        concat_with=" --> hello :)"
    ))
    binder.bind(WineTournamentUC, WineTournamentUCImpl())
