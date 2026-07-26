# HTTP API

The daemon exposes a small REST API on the port configured in
`config/config.yaml` (default 8080).

## Endpoints

### `GET /api/health`

Liveness check.

```json
{"ok": true, "ts": 1714567890.12}
```

### `GET /api/state`

Current state snapshot.

```json
{
  "mode": "cool",
  "fan": "high",
  "setpoint_cool_f": 74.0,
  "setpoint_heat_f": 68.0,
  "room_f": 76.3,
  "outdoor_f": 88.1,
  "last_decision": "cool",
  "in_defrost": false,
  "compressor_active": true,
  "last_update": 1714567890.12,
  "error": ""
}
```

### `POST /api/mode`

```json
{ "mode": "cool", "fan": "high" }
```

- `mode`: `off` | `cool` | `heat` | `fan_only` | `auto`
- `fan`:  `low` | `high` | `auto`

### `POST /api/setpoint`

```json
{ "cool": 74, "heat": 68 }
```

Both setpoints in F. The new values are persisted to `config/config.yaml`.

## Examples

```bash
PI=http://localhost:8080

curl $PI/api/health
curl $PI/api/state | jq

curl -X POST $PI/api/mode \
     -H "Content-Type: application/json" \
     -d '{"mode":"cool","fan":"high"}'

curl -X POST $PI/api/setpoint \
     -H "Content-Type: application/json" \
     -d '{"cool":72,"heat":66}'
```

## Home Assistant

Use a REST sensor for state and a REST command for control:

```yaml
rest_command:
  dometic_mode:
    url: "http://dometic-pi.local:8080/api/mode"
    method: POST
    content_type: "application/json"
    payload: '{"mode": "{{ mode }}", "fan": "{{ fan }}"}'

rest:
  - resource: "http://dometic-pi.local:8080/api/state"
    scan_interval: 10
    sensor:
      - name: "RV Room Temperature"
        value_template: "{{ value_json.room_f | round(1) }}"
        unit_of_measurement: "°F"
        device_class: temperature
```
