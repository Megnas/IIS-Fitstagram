# IIS---Fitstagram
The implementation of an image board/Instagram clone for a university course (Information Systems) was completed in one week by a team of three people.

## Running it

Whole project can be run in docker
### Using Makefile
``` make run ``` - creates ```.env``` file if does not exists and runs the web app in docker
``` make stop ``` - stops docker container
``` make clean ``` - stops docker container and removes all volumes and ```.env``` file

### Using Docker compose
First create ```.env``` file by copying ```env_example``` and then run it with ``` docker compose up ```

## Examples
