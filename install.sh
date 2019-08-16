#!/bin/bash

# Check for python3.7
cmd="python3 -c \"import sys; print('.'.join(map(str, sys.version_info[:2])))\""
if [ python3 2>&1 > /dev/null ] && [ $(eval $cmd) == "3.7" ]; then
    echo "Found python3.7"
else
    echo "Please install Python 3.7"
    exit 1
fi

# Check for pip3.
if command -v pip3 &> /dev/null; then
    printf "Found pip3\n"
else
    printf "Please install python3-pip\n"
    exit 1
fi

# Translate long options to short
# See https://stackoverflow.com/questions/402377/using-getopts-in-bash-shell-script-to-get-long-and-short-command-line-options
for arg
do
    delim=""
    case "$arg" in
       --dev) args="${args}-d ";;
       # pass through anything else
       *) [[ "${arg:0:1}" == "-" ]] || delim="\""
           args="${args}${delim}${arg}${delim} ";;
    esac
done

# Reset the translated args
eval set -- $args

# Parse the options
dev=false
while getopts ":d" opt; do
    case $opt in
        d)
	    printf "Development installation\n"
	    dev=true
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
    esac
done

shift $((OPTIND-1))

venvname="venv"
if [ $# -gt 0 ]; then
   printf "Virtual environment name: $1\n"
   venvname=$1
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

if [[ "$?" != 0 ]]; then
    printf "Failed to install dependencies.\n"
    exit 1
fi

# Install dev dependencies if specified
if [ "$dev" = true ]; then
    printf "Installing dev-dependencies\n"
    pip3 install -r requirements-dev.txt
fi

if [[ "$?" != 0 ]]; then
    printf "Failed to install dev-dependencies\n"
    exit 1
fi

printf "Setting up BlueSky submodule"
git submodule update --init --recursive

printf "Installation successful\n"
printf "To run BlueBird locally:\n"
printf "> source $venvname/bin/activate\n"
printf "> python ./run.py\n"

