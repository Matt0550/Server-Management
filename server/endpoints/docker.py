from dependencies import *

########################
# DOCKER API ENDPOINTS #
########################

router = APIRouter(prefix="/docker", tags=["Docker"])

client = docker.from_env()

# Get all containers
@router.get("/containers")
def get_containers(request: Request, response: Response):
    containers = client.containers.list(all=True)
    container_list = []
    # Append all containers to a list
    for container in containers:
        container_list.append({
            "id": container.id,
            "name": container.name,
            "image": container.image.tags[0],
            "status": container.status,
            "ports": container.ports,
            "labels": container.labels,
            "created": str(container.attrs["Created"])[:-4] + "Z"
        })

    response.status_code = status.HTTP_200_OK

    return {"message": container_list, "status": "success", "code": response.status_code}

# Get a specific container
@router.get("/containers/{container_id}")
def get_container(container_id: str, request: Request, response: Response):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Container not found", "status": "error", "code": response.status_code}

    response.status_code = status.HTTP_200_OK

    return {"message": {
        "id": container.id,
        "name": container.name,
        "image": container.image.tags[0],
        "status": container.status,
        "ports": container.ports,
        "labels": container.labels,
        "created": str(container.attrs["Created"])[:-4] + "Z",
        "command": container.attrs["Config"]["Cmd"],
        "environment": container.attrs["Config"]["Env"],
        "volumes": container.attrs["Mounts"],
        "networks": container.attrs["NetworkSettings"]["Networks"],
        "log": container.logs().decode("utf-8"),
        "stats": container.stats(stream=False),
    }, "status": "success", "code": response.status_code}

# Run a container
@router.post("/containers/run/{container_id}")
def run_container(container_id: str, request: Request, response: Response):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Container not found", "status": "error", "code": response.status_code}

    container.start()

    response.status_code = status.HTTP_200_OK

    return {"message": "Container started", "status": "success", "code": response.status_code}

# Stop a container
@router.post("/containers/stop/{container_id}")
def stop_container(container_id: str, request: Request, response: Response):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Container not found", "status": "error", "code": response.status_code}

    container.stop()

    response.status_code = status.HTTP_200_OK

    return {"message": "Container stopped", "status": "success", "code": response.status_code}

# Restart a container
@router.post("/containers/restart/{container_id}")
def restart_container(container_id: str, request: Request, response: Response):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Container not found", "status": "error", "code": response.status_code}

    container.restart()

    response.status_code = status.HTTP_200_OK

    return {"message": "Container restarted", "status": "success", "code": response.status_code}

# Delete a container
@router.delete("/containers/{container_id}")
def delete_container(container_id: str, request: Request, response: Response):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Container not found", "status": "error", "code": response.status_code}

    container.remove()

    response.status_code = status.HTTP_200_OK

    return {"message": "Container deleted", "status": "success", "code": response.status_code}

# Get all images
@router.get("/images")
def get_images(request: Request, response: Response):
    images = client.images.list(all=True)
    image_list = []
    # Append all images to a list
    for image in images:
        image_list.append({
            "id": image.id,
            "tags": image.tags,
            "created": str(image.attrs["Created"])[:-4] + "Z",
            "size": image.attrs["Size"],
            "virtual_size": image.attrs["VirtualSize"]
        })
        
    response.status_code = status.HTTP_200_OK

    return {"message": image_list, "status": "success", "code": response.status_code}

# Get a specific image
@router.get("/images/{image_id}")
def get_image(image_id: str, request: Request, response: Response):
    try:
        image = client.images.get(image_id)
    except docker.errors.ImageNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Image not found", "status": "error", "code": response.status_code}

    response.status_code = status.HTTP_200_OK

    return {"message": {
        "id": image.id,
        "tags": image.tags,
        "created": str(image.attrs["Created"])[:-4] + "Z",
        "size": image.attrs["Size"],
        "virtual_size": image.attrs["VirtualSize"],
        "history": image.history()
    }, "status": "success", "code": response.status_code}

# Delete an image
@router.delete("/images/{image_id}")
def delete_image(image_id: str, request: Request, response: Response):
    try:
        image = client.images.get(image_id)
    except docker.errors.ImageNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Image not found", "status": "error", "code": response.status_code}

    image.remove()

    response.status_code = status.HTTP_200_OK

    return {"message": "Image deleted", "status": "success", "code": response.status_code}

# Get all networks
@router.get("/networks")
def get_networks(request: Request, response: Response):
    networks = client.networks.list()
    network_list = []
    # Append all networks to a list
    for network in networks:
        network_list.append({
            "id": network.id,
            "name": network.name,
            "driver": network.attrs["Driver"],
            "containers": network.attrs["Containers"],
            "created": str(network.attrs["Created"])[:-4] + "Z",
            "scope": network.attrs["Scope"]
        })

    response.status_code = status.HTTP_200_OK

    return {"message": network_list, "status": "success", "code": response.status_code}

# Get a specific network
@router.get("/networks/{network_id}")
def get_network(network_id: str, request: Request, response: Response):
    try:
        network = client.networks.get(network_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Network not found", "status": "error", "code": response.status_code}

    response.status_code = status.HTTP_200_OK

    return {"message": {
        "id": network.id,
        "name": network.name,
        "driver": network.attrs["Driver"],
        "containers": network.attrs["Containers"],
        "created": str(network.attrs["Created"])[:-4] + "Z",
        "scope": network.attrs["Scope"]
    }, "status": "success", "code": response.status_code}

# Delete a network
@router.delete("/networks/{network_id}")
def delete_network(network_id: str, request: Request, response: Response):
    try:
        network = client.networks.get(network_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Network not found", "status": "error", "code": response.status_code}

    network.remove()

    response.status_code = status.HTTP_200_OK

    return {"message": "Network deleted", "status": "success", "code": response.status_code}

# Get all volumes
@router.get("/volumes")
def get_volumes(request: Request, response: Response):
    volumes = client.volumes.list()
    volume_list = []
    # Append all volumes to a list
    for volume in volumes:
        volume_list.append({
            "id": volume.id,
            "name": volume.name,
            "driver": volume.attrs["Driver"],
            "mountpoint": volume.attrs["Mountpoint"],
            "created": str(volume.attrs["CreatedAt"])[:-4] + "Z",
            "scope": volume.attrs["Scope"]
        })

    response.status_code = status.HTTP_200_OK

    return {"message": volume_list, "status": "success", "code": response.status_code}

# Get a specific volume
@router.get("/volumes/{volume_id}")
def get_volume(volume_id: str, request: Request, response: Response):
    try:
        volume = client.volumes.get(volume_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Volume not found", "status": "error", "code": response.status_code}

    response.status_code = status.HTTP_200_OK

    return {"message": {
        "id": volume.id,
        "name": volume.name,
        "driver": volume.attrs["Driver"],
        "mountpoint": volume.attrs["Mountpoint"],
        "created": str(volume.attrs["CreatedAt"])[:-4] + "Z",
        "scope": volume.attrs["Scope"]
    }, "status": "success", "code": response.status_code}

# Delete a volume
@router.delete("/volumes/{volume_id}")
def delete_volume(volume_id: str, request: Request, response: Response):
    try:
        volume = client.volumes.get(volume_id)
    except docker.errors.NotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Volume not found", "status": "error", "code": response.status_code}

    volume.remove()

    response.status_code = status.HTTP_200_OK

    return {"message": "Volume deleted", "status": "success", "code": response.status_code}
