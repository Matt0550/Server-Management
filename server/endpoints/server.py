from dependencies import *

########################
# SERVER API ENDPOINTS #
########################

router = APIRouter(prefix="/server", tags=["Server"])

# Get server stats (cpu usage, ram usage, disks)


@router.get("/stats")
def get_server_stats(request: Request, response: Response):
    response.status_code = status.HTTP_200_OK
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disks": [
            {
                "name": disk.device,
                "usage": psutil.disk_usage(disk.mountpoint).percent,
                "size": psutil.disk_usage(disk.mountpoint).total,
                "free": psutil.disk_usage(disk.mountpoint).free ,
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

            } for disk in psutil.disk_partitions()
        ],
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

# Get server services
@router.get("/services")
def get_server_services(request: Request, response: Response):
    response.status_code = status.HTTP_200_OK
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
            services.append({
                "pid": pid,
                "name": "Unknown",
                "status": "Access Denied",
                "cpu": "Unknown",
                "memory": "Unknown",
                "cmdline": "Unknown",
                "username": "Unknown",
                "create_time": "Unknown",
            })
            pass
            
    return services

