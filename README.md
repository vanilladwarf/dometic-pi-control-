# dometic-pi-control-
replace dometic heat pump original controll box with RPI
# Dometic 39424.602 - Raspberry Pi Control

A full open-source replacement for the Dometic 3312020.000 control board.
A Raspberry Pi 4/5 (or Zero 2 W) drives the unit's compressors, blowers, and
reversing valve through an 8-channel opto relay HAT and a 4-channel SSR module.

## Features

- Implements the full Dometic protection logic (2-min compressor time delay,
  24 F heat-pump lockout, 4.5-min defrost cycle, 30-s inter-stage delay)
- HTTP API for Home Assistant / Node-RED
- Native MQTT bridge with Home Assistant MQTT Discovery
- systemd service installer
- Full documentation site (mkdocs)
- Multi-Python CI matrix (3.9 through 3.13, plus PyPy)
- Self-hosted Raspberry Pi runner tests against real hardware
- Auto-generated CycloneDX SBOM with CVE scanning
- Renovate + Dependabot for automated dependency updates
- Live CI status dashboard

## Quick start

```bash
git clone https://github.com/yourname/dometic-pi-control.git
cd dometic-pi-control
sudo ./scripts/install.sh
sudo systemctl status dometic
