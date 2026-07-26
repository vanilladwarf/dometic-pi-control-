# Installation guide

> WARNING. Read the safety page before starting. You will be working
> with 115 VAC mains voltage. If you are not qualified, hire a
> licensed HVAC technician.

## Safety

- Always disconnect the 115 VAC breaker before opening the unit
- Verify zero voltage with a non-contact tester
- Wait at least 60 s for the compressor capacitor to discharge
- Wear safety glasses when working over the unit
- Work on a non-conductive surface

## Tools required

- #1 and #2 Phillips screwdrivers
- 4 mm hex driver
- Wire stripper / crimper
- Multimeter rated to 600 V CAT III
- Non-contact voltage tester

## Steps

1. [Prepare the Raspberry Pi](preparing-the-pi.md) — flash, configure I2C/1-Wire
2. [Wire the box](wiring-the-box.md) — connect Pi, relays, SSRs, sensors
3. [Commission the system](commissioning.md) — first power-up, test each function
4. [Bench-test](bench-test.md) — verify the relay HAT before connecting mains

## Quick install (Raspberry Pi OS)

```bash
# 1. Enable I2C and 1-Wire
sudo raspi-config
#   -> Interface Options
#      -> I2C: Yes
#      -> 1-Wire: Yes

# 2. Clone and install
git clone https://github.com/vanilladwarf/dometic-pi-control.git
cd dometic-pi-control
sudo ./scripts/install.sh

# 3. Verify
sudo systemctl status dometic
curl http://localhost:8080/api/health
```

## Quick install (Docker, for development)

```bash
docker compose up
# API at http://localhost:8080
# GPIO and sensors are stubbed
```
