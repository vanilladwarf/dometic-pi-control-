
## File 6: `docs/hardware/README.md`

````markdown
# Hardware overview

## What you are building

A drop-in replacement for the Dometic 3312020.000 control board. The Pi
takes the place of the control board; everything downstream of the 9-pin
connector remains original.

## Block diagram


## Subsystem pages

- [Parts list](parts-list.md) — what to buy, with part numbers
- [Wiring overview](wiring-overview.md) — top-level wiring map
- [Dometic 9-pin connector](wiring-dometic-9pin.md) — pin-by-pin
- [Relays and SSRs](wiring-relays-and-ssr.md) — how to wire each load
- [Power](wiring-power.md) — 5 V buck, fusing, grounding
- [Sensors](wiring-sensors.md) — BME280 and DS18B20

## Safety

This project controls a 115 VAC appliance. Read
[the safety page](../installation/README.md#safety) before doing any wiring.
