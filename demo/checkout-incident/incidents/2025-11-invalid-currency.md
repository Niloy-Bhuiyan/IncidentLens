# INC-2025-11 — invalid currency format

An earlier checkout regression passed `USD_US` to the payment adapter. The gateway adapter accepts ISO-4217 alpha-3 values such as `USD`, not region-qualified tags. The incident produced the `invalid_currency_format` signature. Remediation stripped the region suffix before `create_charge` and added contract tests.

The prior event did not involve a gateway outage; gateway latency and availability were normal.

