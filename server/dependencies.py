import json, datetime, os
from typing import Dict
import threading
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Query, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter
import docker
from pydantic import BaseModel, Field


# # CONTAINERS
# class Container(BaseModel):
#     name: str = Field(description="The name of the container", example="test")
#     image: str = Field(description="The image of the container", example="test")
