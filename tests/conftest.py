import os
import shutil

# Configure testcontainers to use Podman when Docker is not available
if not shutil.which("docker"):
    os.environ.setdefault("DOCKER_HOST", "npipe:////./pipe/podman-machine-default")
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
