from fastapi import status


class BaseAppException(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class PasswordError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password.")


class UserNotFoundError(BaseAppException):
    def __init__(self, user_id: int | None = None, email: str | None = None):
        if user_id is not None:
            detail = f"User with id {user_id} not found."
        elif email:
            detail = f"User with email '{email}' not found."
        else:
            detail = "User not found."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserAlreadyError(BaseAppException):
    def __init__(self, email: str | None = None):
        detail = f"User with email '{email}' already exists." if email else "User already exists."
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UsersNotFoundError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found.")


class PermissionDeniedError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


class TokenExpiredError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")


class TokenInvalidError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid.")


class TripNotFoundError(BaseAppException):
    def __init__(self, trip_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip {trip_id} not found.")


class TripsNotFoundError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Trips not found.")


class TripStatusError(BaseAppException):
    def __init__(self, trip_id: int):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Trip {trip_id} invalid status transition.")


class ForbiddenStatus(BaseAppException):
    def __init__(self, trip_id: int):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access to trip {trip_id} is forbidden.")


class DriversNotFoundError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="No drivers available nearby.")


class RatingAlreadyExistsError(BaseAppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Rating for this trip already exists.")


class PaymentMethodNotFoundError(BaseAppException):
    def __init__(self, user_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment method not found for user {user_id}.")
