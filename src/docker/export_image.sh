
VERSION_TAG="v$(date +%Y%m%d%H%M%S)"

# Set the container ID
CONTAINER_ID=$(docker ps -q --filter ancestor=cancer_ae_dash:latest)

# Commit container to an image named cancer_ae_dash:latest
docker commit $CONTAINER_ID cancer_ae_dash:$VERSION_TAG
docker tag cancer_ae_dash:$VERSION_TAG cancer_ae_dash:latest

# Save image to a tar file
docker save -o cancer_ae_dash_latest.tar cancer_ae_dash:latest