# Dometic 39424.602 — Raspberry Pi Control

Open-source replacement for the Dometic 3312020.000 control board. A
Raspberry Pi drives the unit's compressors, blowers, and reversing valve
through a relay HAT and SSR module — no Modbus, no proprietary protocol.

## What it does

- Reads room and outdoor temperature
- Runs a hysteresis thermostat with the same protection logic as the
  original Dometic 3312020.000 board:
  - 2-minute compressor cooldown
  - 24 F heat-pump lockout (configurable)
  - 4.5-minute defrost cycle (when outdoor is 24-42 F)
  - 30-second inter-stage delay
- Drives the 9-pin connector to the unit (compressors, blowers, RV)
- Exposes an HTTP API on port 8080
- Publishes state to MQTT (Home Assistant auto-discovers the climate entity)

## Quick start

### On a Raspberry Pi

```bash
git clone https://github.com/vanilladwarf/dometic-pi-control.git
cd dometic-pi-control
sudo ./scripts/install.sh
sudo systemctl status dometic
