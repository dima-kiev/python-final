from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.schemas import (
    UserCreate,
    TokenModel,
    UserResponse,
    RequestEmail,
    TokenRefreshRequest,
)
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    Hash,
    get_email_from_token,
    generate_temp_password,
    verify_refresh_token,
)
from src.services.users import UserService
from src.services.email import send_email, send_reset_password_email
from src.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/forget_password",
    description="No more than 2 requests per minute",
)
@limiter.limit("2/minute")
async def forget_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Request email with the temporary password.

    Args:
        body (RequestEmail): Email address where the code is going to be sent.

    Returns:
        dict: Confirmation message.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        if not user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is not confirmed",
            )

        generated_password = generate_temp_password()
        hashed_password = Hash().get_password_hash(generated_password)
        await user_service.update_hashed_password(body.email, hashed_password)

        background_tasks.add_task(
            send_reset_password_email, body.email, generated_password
        )
    return {
        "message": "If this user exists in our database, we have sent them an email with temporary password"
    }


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Request new email verification.

    Args:
        body (RequestEmail): Email to verify.

    Returns:
        dict: Confirmation message.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        if user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already confirmed",
            )
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {
        "message": "If this user exists in our database, we have sent them a confirmation email"
    }


@router.get("/confirm_email/{token}")
async def confirm_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Verify email.

    Args:
        token (str): Email JWT.

    Returns:
        dict: Confirmation message.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already confirmed"
        )
    await user_service.confirm_email(email)
    return {"message": "Email was confirmed"}


# Реєстрація користувача
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register user.

    Args:
        user_data (UserCreate): The data to be assigned to the new User.

    Returns:
        UserResponse: Registered User.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=TokenModel)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Login user.

    Args:
        form_data (OAuth2PasswordRequestForm): Standard form data for login.

    Returns:
        TokenModel: User's tokens.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )

    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    user = await user_service.update_refresh_token(user.email, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=TokenModel)
async def new_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    user = await verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }
