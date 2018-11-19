
# Development Notes

General notes on developing with BlueSky / Flask etc.


## Debugging Flask

Need to properly investigate Flasks console [logging](http://flask.pocoo.org/docs/1.0/logging/) functionality. In the meantime, you can write to the server output with `print('text', file=sys.stderr)`. Messages seem to flush through in batches though, so really not an ideal solution.

Flask supports live code reloading, and this works well when running with docker. This only appears to function (I think) with code that Flask directly manages though. So changes to the BlueSky client code won't be refreshed for example.


## Running BlueSky in docker

Haven't been able to achieve this yet due to BlueSky requiring pyopengl-accelerate for the GUI bits, even though we only want to run the sim/server in docker. Can hopefully get it working if the requirements file is split, and the initial BlueSky.py startup script is modified to handle it. (see [here](https://stackoverflow.com/questions/17803829/how-to-customize-a-requirements-txt-for-multiple-environments)).

## General BlueSky issues

Can feed all this back to the developers and maybe make our own pull requests with fixes.

No versions specified for any of the required packages. Or what versions of Python 2.X/3.X are supported. Have run into numerous issues with mismatches between expected/installed package versions, and finding 3.7 code when a required library only supports 3.6. See [PEP-508](https://www.python.org/dev/peps/pep-0508/#environment-markers).

Would be useful in general to tidy up BlueSky's dependencies so that only libraries required for the selected mode are checked for.

The `check.py` file is missing some of the requirements. It can report everything fine even if BS crashes on startup.

No handling of a timeout in the Client->Server connection. Will hang forever if no server present.



