DOCKER_NAME=iis-fitstagram

.PHONY: docker docker-run docker-build clean zip

# Main target
docker: docker-build docker-run

# Run the Docker container
docker-run:
	docker run --name "$(DOCKER_NAME)" -d -p 80:5000 --network=main $(DOCKER_NAME)

# Build the Docker image
docker-build:
	docker build -t $(DOCKER_NAME) .

# Optionally, you can add a clean target to stop and remove the container
clean:
	docker stop "$(DOCKER_NAME)" || true
	docker rm "$(DOCKER_NAME)" || true

zip:
	zip xvacla37.zip *.py modules/*.py templates/*.html requirements.txt doc.html static/* static/images/* *.svg