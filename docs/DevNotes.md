
# Development Notes

General notes on developing with BlueSky / Flask etc.


## Debugging Flask

Need to properly investigate Flasks console [logging](http://flask.pocoo.org/docs/1.0/logging/) functionality. In the meantime, you can write to the server output with the utility function `bluebird.utils.debug.errprint(text)`. Messages seem to flush through in batches though, so really not an ideal solution.

Flask supports live code reloading, and this works well when running with docker. This only appears to function (I think) with code that Flask directly manages though. So changes to the BlueSky client code won't be refreshed for example.
