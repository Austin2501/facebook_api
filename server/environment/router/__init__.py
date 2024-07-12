import os
from fastapi import APIRouter

current_environment = os.environ.get('env_name')

__sample_path = os.environ.get('sample_controller')
sample_router = APIRouter(prefix=__sample_path)

