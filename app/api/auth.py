from typing import Optional

from fastapi.security.api_key import APIKeyHeader
from fastapi import HTTPException, Security
from starlette.status import HTTP_401_UNAUTHORIZED
from decouple import config

api_key_scheme = APIKeyHeader(name="API-KEY", auto_error=False)
jwt_token_scheme = APIKeyHeader(name="Authorization", auto_error=False)


async def validate_apikey_request(
        api_key: str = Security(api_key_scheme),
) -> Optional[bool]:
    """Validate a request with given email and api key
    to any endpoint resource
    """
    # verify email & API key
    if api_key == config("SERVICE_API_KEY"):
        return True
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
        )
