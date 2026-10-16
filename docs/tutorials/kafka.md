# Kafka

For engineers who feed a Kafka topic. It teaches an event stream as JSON lines, and the producer block that sends the same events to a broker.

Get the file:

```bash
rand-engine get-started kafka
```

It writes the file to the current directory. `--out DIR` writes it to `DIR` instead, created when missing. An existing file is never overwritten.

```python no-run
--8<-- "rand_engine/cases/kafka.py.txt"
```

Running it as-is prints 100 events, one JSON line each. It needs no broker and no Kafka client.

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
