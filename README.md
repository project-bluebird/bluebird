
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
- `localhost:5001/api/v1/cre` - Create an aircraft. Must provide the following JSON body:
```json
{
  "acid": "test1234",
  "type": "B744",
  "lat": "0",
  "lon": "0",
  "hdg": "0",
  "alt": "FL250",
  "spd": "250"
}
```
