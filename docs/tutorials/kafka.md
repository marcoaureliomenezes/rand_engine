# Kafka

For engineers who feed a Kafka topic. It teaches an event stream as JSON lines, and the producer block that sends events to a broker. Each `stream_dict` call continues the seeded sequence, so a second call yields different payloads under the same `event_id` range.

## Prerequisite and run

Install `rand-engine`, then scaffold and run the file. Its default path needs neither a broker nor
`kafka-python`:

Get the file:

```bash
pip install rand-engine
rand-engine get-started kafka
python kafka-example.py
```

It writes `kafka-example.py` to the current directory. `--out DIR` writes it to `DIR` instead,
created when missing. An existing file is never overwritten. Running it as-is prints 100 JSON
events, one line per event, to stdout.

```python no-run
--8<-- "rand_engine/cases/kafka.py.txt"
```

## Enable the producer

The producer is off by default. To send the events to a topic named `events`:

1. Install the client: `pip install kafka-python`.
2. In the file, set `SEND_TO_KAFKA = True` and set `BOOTSTRAP_SERVERS` to your broker.
3. Run the file again.

## What it shows

- **Describe**: the event spec, and the two switches, `SEND_TO_KAFKA` and `BOOTSTRAP_SERVERS`.
- **Print**: 100 events from `stream_dict`, one JSON line each. The wall-clock `timestamp_created` is dropped, so the seeded `ts` stays the event time.
- **Producer**: the block that runs only when `SEND_TO_KAFKA` is set.

## Next steps

- [Data generator](../1_DATA_GENERATOR.md): `stream_dict` and the other ways to generate.
- [Reference](../reference.md): the `DataGenerator` API.
