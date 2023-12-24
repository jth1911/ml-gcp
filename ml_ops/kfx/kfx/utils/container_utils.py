import subprocess
import logging
logger = logging.getLogger("logger")
logging.basicConfig(level=logging.INFO)

def build_container(container_uri,dockerfile_uri="."):
    result = subprocess.run(['docker','build',dockerfile_uri,'-t',container_uri])
    if result.stderr:
        logger.error("error running docker build")
        logger.error(f"stderr: {result.stderr}")
        raise RuntimeError(f"Something went wrong building {container_uri}")

def push_container(container_uri):
    result = subprocess.run(['docker','push',container_uri])
    if result.stderr:
        logger.error("error running docker build")
        logger.error(f"stderr: {result.stderr}")
        raise RuntimeError(f"Something went wrong pushing {container_uri}")
    