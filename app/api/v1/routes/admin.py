from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Security

from app.api.v1.routes.user import request_reset_password
from app.database.dependencies import sessDep
from app.functions.exceptions import conflict
from app.models.auth.functions import authorize
from app.models.auth.role import Role
from app.models.user import User
from app.models.user.schemas import UserIn, UserOut

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Security(authorize, scopes=[Role.ADMIN])],
)


@router.post("/user", response_model=UserOut, status_code=201)
async def create_user(
    *,
    async_session: sessDep,
    user_in: UserIn,
    send_email: bool = True,
    bt: BackgroundTasks
):
    if await User.find(async_session=async_session, email=user_in.email, raise_=False):
        raise conflict(msg="User already exists")
    user = await User(**user_in.model_dump()).save(async_session)
    if send_email:
        await request_reset_password(async_session, email=user.email, bt=bt)
    return user


@router.get("/user", response_model=list[UserOut], status_code=200)
async def get_users(async_session: sessDep):
    return await User.all(async_session)


@router.get("/user/{id}", response_model=UserOut, status_code=200)
async def get_user(async_session: sessDep, id: UUID):
    return await User.get(async_session, id)


@router.delete("/user/{id}", status_code=204)
async def delete_user(async_session: sessDep, id: UUID):
    user = await User.get(async_session, id)
    await user.delete(async_session)


@router.put("/user/{id}", response_model=UserOut, status_code=200)
async def update_user(async_session: sessDep, id: UUID, user_in: UserIn):
    user = await User.get(async_session, id)
    return await user.update(async_session, **user_in.model_dump(exclude_unset=True))
