#!/bin/bash

# Check for python3.
if command -v python3 &>/dev/null; then
    printf "Found python3\n"
else
    printf "Please install python3\n"
    exit 1
fi

# Check for pip3.
if command -v pip3 &>/dev/null; then
    printf "Found pip3\n"
else
    printf "Please install python3-pip\n"
    exit 1
fi

if [ $# -eq 1 ]; then
    venvname=$1
else
    venvname="venv"
fi

if [ -e $venvname ]; then
    printf "Virtual environment %s already exists.\nPlease remove or specify a different name as arg1.\n" $venvname
    exit 1
fi

# Check for virtualenv
if command -v virtualenv &>/dev/null; then
    printf "Found virtualenv\n"
else
    printf "Please install virtualenv\n"
    exit 1
fi

# Create a virtual environment.
printf "Creating virtual environment: $venvname\n"
pip3 install --upgrade virtualenv
virtualenv -p python3 $venvname

printf "Activating virtual environment\n"
source $venvname/bin/activate

printf "Installing dependencies\n"
pip3 install -r requirements.txt

status=$?
if [[ $status != 0 ]]; then
    printf "Failed to install dependencies.\n"
    exit 1
fi

printf "Installation successful\n"
printf "To run BlueBird locally:\n"
printf "> source $venvname/bin/activate\n"
printf "> python ./run.py\n"

