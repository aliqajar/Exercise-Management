from fastapi import HTTPException, status

class ErrorCode:
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    ALREADY_EXISTS = "ALREADY_EXISTS"

class ErrorMessage:
    EXERCISE_NOT_FOUND = "Exercise not found"
    USER_NOT_FOUND = "User not found"
    UNAUTHORIZED_ACCESS = "Not authorized to access this resource"
    UNAUTHORIZED_UPDATE = "Not authorized to update this resource"
    UNAUTHORIZED_DELETE = "Not authorized to delete this resource"
    INVALID_INTERACTION_TYPE = "Invalid interaction type. Must be 'favorites' or 'saves'"
    INVALID_UUID = "Invalid UUID format"

def not_found_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
        headers={"X-Error-Code": ErrorCode.NOT_FOUND}
    )

def unauthorized_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"X-Error-Code": ErrorCode.UNAUTHORIZED}
    )

def forbidden_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
        headers={"X-Error-Code": ErrorCode.FORBIDDEN}
    )

def validation_error(detail: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"X-Error-Code": ErrorCode.VALIDATION_ERROR}
    )

def already_exists_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
        headers={"X-Error-Code": ErrorCode.ALREADY_EXISTS}
    ) 