from fastapi import Request
from schema.errors import Errors, throw_error
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import status


from server.logger import Logger
logger = Logger.get_logger(__name__)

def validation_exception_handler(_: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    message = '{} {}'.format('.'.join(error['loc']), error['msg'])
    return throw_error(status= status.HTTP_400_BAD_REQUEST, message="Validation error", error_code= 4000, error= message)


async def exception_handler(req: Request, exc: Exception):
    func_handler = req.state.func_name
    logger.error('An error occured during {} handling. Error: {}'.format(func_handler, exc))
    return throw_error(status= status.HTTP_500_INTERNAL_SERVER_ERROR, message= "An error occured", error_code= 5000, error= str(exc) )
