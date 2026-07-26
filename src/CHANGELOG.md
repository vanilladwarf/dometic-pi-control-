# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-XX-XX

### Added
- Full Pi-driven replacement for the Dometic 3312020.000 control board
- 2-minute compressor cooldown
- 24 F heat-pump lockout
- 4.5-minute defrost cycle
- 30-second inter-stage delay
- HTTP API on port 8080 (health, state, mode, setpoint)
- MQTT bridge with Home Assistant discovery
- systemd service installer
- Bench-test and diagnostic scripts
- Multi-Python CI matrix (3.9 - 3.13)
- Multi-arch Docker image (amd64 + arm64)
- CycloneDX SBOM with CVE scanning
- Comprehensive documentation
