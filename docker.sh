#!/bin/bash

# FlameCare Backend Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="flamecare-backend"
CONTAINER_NAME="flamecare-backend"
PORT="5000"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME .
    print_status "Docker image built successfully!"
}

# Function to run container
run_container() {
    print_status "Starting container: $CONTAINER_NAME"
    
    # Stop existing container if running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_warning "Stopping existing container..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
    fi
    
    # Run new container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:5000 \
        -v "$(pwd)/static/uploads:/app/static/uploads" \
        $IMAGE_NAME
    
    print_status "Container started successfully!"
    print_status "API is available at: http://localhost:$PORT"
}

# Function to view logs
view_logs() {
    print_status "Viewing container logs..."
    docker logs -f $CONTAINER_NAME
}

# Function to stop container
stop_container() {
    print_status "Stopping container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    print_status "Container stopped!"
}

# Function to enter container shell
shell() {
    print_status "Entering container shell..."
    docker exec -it $CONTAINER_NAME /bin/bash
}

# Function to test API
test_api() {
    print_status "Testing API endpoints..."
    
    # Test root endpoint
    echo "Testing root endpoint..."
    curl -s http://localhost:$PORT/ | jq .
    
    echo -e "\nTesting fluid calculator..."
    curl -s -X POST http://localhost:$PORT/api/test-fluid | jq .
}

# Function to clean up Docker resources
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove container if exists
    if docker ps -a -q -f name=$CONTAINER_NAME | grep -q .; then
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
    fi
    
    # Remove image if exists
    if docker images -q $IMAGE_NAME | grep -q .; then
        docker rmi $IMAGE_NAME
    fi
    
    print_status "Cleanup completed!"
}

# Main script logic
case "$1" in
    build)
        build_image
        ;;
    run)
        build_image
        run_container
        ;;
    start)
        run_container
        ;;
    logs)
        view_logs
        ;;
    stop)
        stop_container
        ;;
    restart)
        stop_container
        run_container
        ;;
    shell)
        shell
        ;;
    test)
        test_api
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "Usage: $0 {build|run|start|logs|stop|restart|shell|test|cleanup}"
        echo ""
        echo "Commands:"
        echo "  build     - Build the Docker image"
        echo "  run       - Build and run the container"
        echo "  start     - Start the container (without building)"
        echo "  logs      - View container logs"
        echo "  stop      - Stop and remove the container"
        echo "  restart   - Stop and start the container"
        echo "  shell     - Enter container shell"
        echo "  test      - Test API endpoints"
        echo "  cleanup   - Remove container and image"
        exit 1
        ;;
esac
