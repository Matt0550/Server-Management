
from fastapi import FastAPI
from slowapi import Limiter
limiter = Limiter(key_func="")
app = FastAPI()