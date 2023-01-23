import modules
from dependencies import *

import sys
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


modules.limiter = Limiter(key_func=get_remote_address, default_limits=["3/5seconds", "10/minute"])

modules.app = FastAPI(title="Test", description="Test")

app = modules.app

app.state.limiter = modules.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["http://127.0.0.1/", "http://localhost", "http://192.168.1.75", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

##################
# ERROR HANDLERS #
##################

# Handle the 404 error. Use HTTP_exception_handler to handle the error
@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(content={"message": "Not found", "status": "error", "code": exc.status_code}, status_code=exc.status_code)
    elif exc.status_code == 405:
        return JSONResponse(content={"message": "Method not allowed", "status": "error", "code": exc.status_code}, status_code=exc.status_code)
    else:
        # Just use FastAPI's built-in handler for other errors
        return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    print(exc.errors())

    if exc.errors()[0]["type"] == "value_error.any_str.max_length":
        limit = str(exc.errors()[0]["ctx"]["limit_value"])
        return JSONResponse(content={"message": "The value entered is too long. Max length is " + limit, "status": "error", "code": status_code}, status_code=status_code)
    elif exc.errors()[0]["type"] == "value_error.missing":
        missing = []
        for error in exc.errors():
            try:
                missing.append(error["loc"][1])
            except:
                missing.append(error["loc"][0])

        return JSONResponse(content={"message": "One or more fields are missing: " + str(missing), "status": "error", "code": status_code}, status_code=status_code)
    else:
        return JSONResponse(content={"message": exc.errors()[0]["msg"], "status": "error", "code": status_code}, status_code=status_code)

# Dynamic imports
endpoints = []
for endpoint in os.listdir("endpoints"):
    if endpoint.endswith(".py") and endpoint.startswith("OFF_"):
        print("Endpoint " + endpoint + " is disabled")
        continue
    if endpoint.endswith(".py") and endpoint != "__init__.py":
        endpoints.append(endpoint[:-3])

for endpoint in endpoints:
    try:
        __import__("endpoints." + endpoint)
        app.include_router(getattr(sys.modules["endpoints." + endpoint], "router"))
    except Exception as e:
        print("Error loading endpoint " + endpoint + ": " + str(e))
        
start_time = datetime.datetime.now() # For the uptime

######################################
############## HOME API ##############
######################################
@app.get("/status")
def api_status(request: Request, response: Response):
    # Get the API uptime without microseconds
    uptime = datetime.datetime.now() - start_time
    uptime = str(uptime).split(".")[0]

    url = request.url
    url = url.scheme + "://" + url.netloc

    response.status_code = status.HTTP_200_OK

    return {"message": "Online", "uptime": uptime, "status": "success", "code": response.status_code, "url": url}

@app.get('/')
def home(request: Request, response: Response):
    return api_status(request, response)