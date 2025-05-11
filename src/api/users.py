from fastapi import APIRouter, Depends, Request, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.schemas import UserResponse, RequestPassword
from src.database.models import User
from src.services.auth import get_current_user, get_current_admin_user
from src.database.db import get_db
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.conf.config import settings
from src.services.auth import Hash


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me",
    response_model=UserResponse,
    description="No more than 10 requests per minute",
)
@limiter.limit("10/minute")
async def me(request: Request, user: UserResponse = Depends(get_current_user)) -> User:
    """
    Get current User.

    Returns:
        User: Current User.
    """
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserResponse = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update a current User's avatar URL.

    Args:
        file (UploadFile): The file to upload to Cloudinary which URL will be user for User avatar URL.

    Returns:
        User: The User with updated avatar.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.patch(
    "/password",
    response_model=UserResponse,
    description="No more than 2 requests per minute",
)
@limiter.limit("2/minute")
async def update_user_password(
    request: Request,
    body: RequestPassword,
    user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update a current User's password.

    Args:
        body (RequestPassword): RequestPassword body.

    Returns:
        User: The User with updated password.
    """
    user_service = UserService(db)

    if Hash().verify_password(body.old_password, user.hashed_password):
        await user_service.update_hashed_password(
            user.email, Hash().get_password_hash(body.new_password)
        )

    return user
