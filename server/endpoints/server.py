from dependencies import *

########################
# SERVER API ENDPOINTS #
########################

router = APIRouter(prefix="/server", tags=["Server"])

STREAM_DELAY = 10 # seconds
RETRY_TIMEOUT = 15000 # milliseconds

def getServerStats():
    disks = []
    for disk in psutil.disk_partitions():
        try:
            disks.append({
                "name": disk.device,
                "usage": psutil.disk_usage(disk.mountpoint).percent,
                "size": psutil.disk_usage(disk.mountpoint).total,
                "free": psutil.disk_usage(disk.mountpoint).free,
                "used": psutil.disk_usage(disk.mountpoint).used,
                "mountpoint": disk.mountpoint,
                "fstype": disk.fstype,
                "opts": disk.opts,
                "type": "removable" if disk.device.startswith("/dev/sd") else "fixed",
                "gb": {
                    "size": round(psutil.disk_usage(disk.mountpoint).total / 1024 / 1024 / 1024, 2),
                    "free": round(psutil.disk_usage(disk.mountpoint).free / 1024 / 1024 / 1024, 2),
                    "used": round(psutil.disk_usage(disk.mountpoint).used / 1024 / 1024 / 1024, 2)
                }
            })
        except:
            disks.append({
                "name": disk.device,
                "usage": 0,
                "size": 0,
                "free": 0,
                "used": 0,
                "mountpoint": disk.mountpoint,
                "fstype": disk.fstype,
                "opts": disk.opts,
                "type": "removable" if disk.device.startswith("/dev/sd") else "fixed",
                "gb": {
                    "size": 0,
                    "free": 0,
                    "used": 0
                }
            })

    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disks": disks,
        "uptime": str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())),
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": platform.system(),
        "arch": platform.machine(),
        "network": {
            "sent": psutil.net_io_counters().bytes_sent,
            "recv": psutil.net_io_counters().bytes_recv,
            "gb": {
                "sent": round(psutil.net_io_counters().bytes_sent / 1024 / 1024 / 1024, 2),
                "recv": round(psutil.net_io_counters().bytes_recv / 1024 / 1024 / 1024, 2)
            }
        }
    }

# Get server stats (cpu usage, ram usage, disks, etc)
@router.get("/stats")
def get_server_stats(request: Request, response: Response):
    response.status_code = status.HTTP_200_OK
    return getServerStats()

# Get server temperature
@router.get("/temperatures")
def get_server_temperatures(request: Request, response: Response):
    # Check os
    if platform.system() == "Linux":
        # Temperatures
        temperatures = []
        for sensor in psutil.sensors_temperatures():
            for temp in psutil.sensors_temperatures()[sensor]:
                temperatures.append({
                    "label": temp.label,
                    "current": temp.current,
                    "high": temp.high,
                    "critical": temp.critical
                })
        response.status_code = status.HTTP_200_OK
        return temperatures

    else:
        response.status_code = status.HTTP_501_NOT_IMPLEMENTED
        return {
            "error": "This endpoint is not implemented for your OS"
        }
    
# Stream server stats (cpu usage, ram usage, disks, etc) using Server-Sent Events 
@router.get("/stats/stream")
async def stream_server_stats(request: Request, response: Response):
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            yield {
                    "id": "1",
                    "event": "server_stats",
                    "retry": RETRY_TIMEOUT,
                    "data": json.dumps(getServerStats())
            }

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())