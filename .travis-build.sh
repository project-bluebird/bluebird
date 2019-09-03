#!/bin/bash
set -ev
cd $BLUEBIRD_HOME
# echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
# If CI on master branch then tag with latest
if [ $TRAVIS_BRANCH = "master" ]; then
    docker build --tag=bluebird .
    docker tag twitcher turinginst/bluebird:latest
    docker push turinginst/bluebird:latest
fi
# If CI on release branch branch then tag with that release number
if [ $TRAVIS_OS_NAME = linux ]; then
    echo $TRAVIS_BRANCH
    # docker build --tag=bluebird .
    # docker tag twitcher turinginst/bluebird:1.3.0
    # docker push turinginst/bluebird:1.3.0
fi
