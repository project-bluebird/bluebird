
# Docker Build

Notes for building and publishing the BlueBird docker image to the `turinginst` DockerHub.

For this example, assume we wish to publish version `1.0.0`, which has been tagged in Git. It may be best to clone a
fresh copy of the repo into a temporary directory to avoid any local changes being included in the image:

```bash
> cd ~/tmp/
> if [ -d bluebird ]; then rm -Rf bluebird ; fi
> git clone git@github.com:alan-turing-institute/bluebird.git
...
> cd bluebird/
> git checkout 1.0.0
```

Run our tests to verify:

```bash
> chmod +x ./install.sh
> ./install.sh --dev
> source venv/bin/activate
> pytest -sv tests/
```

Now we can build, tag, and push the Docker image:

```bash
> docker build . --tag turinginst/bluebird:1.0.0 --tag turinginst/bluebird:latest
...
> docker push turinginst/bluebird:1.0.0
> docker push turinginst/bluebird:latest
```

## Notes and TODO

- TODO: This can be setup to run automatically via DockerHub automated builds
