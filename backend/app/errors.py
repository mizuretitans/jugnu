from fastapi import HTTPException


class ApiError(HTTPException):
    """Error with a stable machine-readable code the frontend can act on."""

    def __init__(self, status: int, code: str, message: str, **extra: object) -> None:
        super().__init__(status, {"code": code, "message": message, **extra})


def not_found(what: str = "Not found") -> ApiError:
    return ApiError(404, "not_found", what)
