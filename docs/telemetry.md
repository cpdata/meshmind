# Telemetry & Observability

MeshMind provides lightweight observability utilities under `meshmind.core.observability` to trace pipeline behaviour.

## Telemetry API

- `telemetry.reset()`: clear counters/gauges (used in tests).
- `telemetry.increment(name, value=1.0, tags=None)`: bump a counter.
- `telemetry.gauge(name, value, tags=None)`: record the latest gauge value.
- `telemetry.timer(name, tags=None)`: context manager to measure elapsed time.
- `telemetry.snapshot()`: return a dictionary of counters/gauges/timers for inspection.

## Instrumented Components

- `meshmind.pipeline.preprocess.score_importance`: records importance distribution metrics.
- `meshmind.pipeline.compress.compress`: wraps compression attempts to measure latency and failure rates.
- `meshmind.pipeline.store` and `meshmind.tasks.scheduled`: emit counters for stored items and maintenance plans.
- Observability hooks are intentionally dependency-free to keep tests deterministic.

## Integrations

- For production use, wrap the telemetry API with adapters that forward metrics to Prometheus, StatsD, or logging
  systems.
- Configure logging handlers (see `logging` usage throughout the pipeline modules) to integrate with your preferred log
  aggregation stack.

## Best Practices

- Tag metrics with `namespace` when running multi-tenant workloads.
- Reset telemetry within tests to avoid cross-test contamination.
- Extend the telemetry module with thread-safe transports if moving beyond single-process deployments.
