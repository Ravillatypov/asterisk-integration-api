exception_codes = {
    0: 'Unknown exception',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not found',
    1000: 'Data not found',
    1001: 'The username is already taken',
    1002: 'Username or password is invalid',
}


class ApiException(Exception):
    code = 0
    status_code = 500


class DataNotFoundException(ApiException):
    code = 1000
    status_code = 400


class UsernameIsUsedException(ApiException):
    code = 1001
    status_code = 400


class PasswordIsInvalidException(ApiException):
    code = 1002
    status_code = 400
