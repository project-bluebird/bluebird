
# BlueBird

Server to communicate with NATS air traffic simulator and BlueSky

## Initial Prototype

See [here](docs/InitialProto.md).

## Usage

Connects to a running BlueSky simulation

```bash
> docker-compose build
> docker-compose up
```

Currently available commands are `IC` and `POS`. Example:

- `localhost:5001/api/v1/ic/ic` - Reset the sim to the start of the last loaded scenario
- `localhost:5001/api/v1/pos/1234` - Get POS info on aircraft `1234`