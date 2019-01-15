#!/bin/bash

# Build the BlueSky image from the submodule
git submodule init
git submodule update
docker build ./bluesky --tag=bluesky

# Now run both BlueSky and BlueBird using docker-compose
docker-compose build
docker-compose up
