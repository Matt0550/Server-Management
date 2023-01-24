from dependencies import *

##########################
# SERVICES API ENDPOINTS #
##########################

router = APIRouter(prefix="/services", tags=["Services"])


# Get services
@router.get("/all")
def get_services(request: Request, response: Response):
    # Pids
    pids = psutil.pids()
    # Services
    services = []
    for pid in pids:
        try:
            p = psutil.Process(pid)
            services.append({
                "pid": pid,
                "name": p.name(),
                "status": p.status(),
                "cpu": p.cpu_percent(),
                "memory": p.memory_percent(),
                "cmdline": p.cmdline(),
                "username": p.username(),
                "create_time": p.create_time(),                                            
                                     
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Add to list of services
            # services.append({
            #     "pid": pid,
            #     "name": "Unknown",
            #     "status": "Access Denied",
            #     "cpu": "Unknown",
            #     "memory": "Unknown",
            #     "cmdline": "Unknown",
            #     "username": "Unknown",
            #     "create_time": "Unknown",
            # })
            pass
    response.status_code = status.HTTP_200_OK

    return services

# Stop service
@router.post("/stop/{pid}")
def stop_service(request: Request, response: Response, pid: int):
    try:
        p = psutil.Process(pid)
        p.terminate()
        response.status_code = status.HTTP_200_OK
        return {"status": "success", "message": "Service stopped"}
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        response.status_code = status.HTTP_200_OK
        return {"status": "error", "message": "Service not found"}
    
# Start service
@router.post("/start/{pid}")
def start_service(request: Request, response: Response, pid: int):
    try:
        p = psutil.Process(pid)
        p.resume()
        response.status_code = status.HTTP_200_OK
        return {"status": "success", "message": "Service started"}
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        response.status_code = status.HTTP_200_OK
        return {"status": "error", "message": "Service not found"}