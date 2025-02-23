import logging
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes

from app.database.dependencies import sessDep
from app.functions.exceptions import forbidden, unauthorized_basic
from app.functions.limiter import rate_limiter
from app.models.auth.role import Role
from app.models.auth.schemas import TokenDecode, TokenEncode
from app.models.auth.schemes import oauth2_scheme
from app.models.auth.token import Token
from app.models.user import User

logger = logging.getLogger(__name__)


class Authenticate:
    def __init__(self, load_relationships: bool = True) -> None:
        self.load_relationships = load_relationships

    async def __call__(
        self, async_session: sessDep, credentials: OAuth2PasswordRequestForm = Depends()
    ) -> User:
        user = await User.find(
            async_session,
            email=credentials.username,
            raise_=False,
            relationships=[User.posts, User.tags] if self.load_relationships else None,
        )
        if not user or not user.check_password(credentials.password):
            raise unauthorized_basic()
        elif user.verified is False:
            raise forbidden("User not verified. Request reset password.")
        logger.info(f"Authenticating user id:{user.id} and email:{user.email}")
        return user


async def authenticate_and_token(
    user: User = Depends(Authenticate(load_relationships=False)),
) -> TokenEncode:
    logger.info(f"Generating token for user id:{user.id} and email:{user.email}")
    return Token(id=user.id, scope=user.scope).encode()


def authorize(
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: Annotated[SecurityScopes, Depends],
) -> TokenDecode:
    decoded_token = Token.decode(
        token=token, scope=[Role(i) for i in security_scopes.scopes]
    )
    logger.info(
        f"Authorizing user ID: {decoded_token.id} with scopes: {decoded_token.scope}"
    )
    return decoded_token


def authorize_limited(token: Annotated[TokenDecode, Depends(authorize)]) -> TokenDecode:
    rate_limiter(token.id.hex)
    return token


async def authorize_and_load(
    async_session: sessDep, token: Annotated[TokenDecode, Depends(authorize)]
) -> User:
    user = await User.get(
        async_session, id=token.id, relationships=[User.posts, User.tags]
    )
    logger.info(f"Authorizing and loading user id:{token.id} and email:{user.email}")
    return user
