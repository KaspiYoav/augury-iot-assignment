# Augury Home Assignment – IoT Simulation + Robot Framework

A local, in-memory simulation of Nodes (gateways) and Endpoints (sensors),
with a fake API (`AuguryAPI`) and Robot Framework end-to-end tests.

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3.9+.

## Run the tests

```bash
python -m robot tests                 # all tests
python -m robot --include dfu tests   # only DFU
python -m robot --include ota tests   # only OTA
```

(`python -m robot` is used so it works even if `robot` is not on PATH.)
Reports: `log.html`, `report.html`, `output.xml`.

## Project structure

```
augury_iot/
  config.py   constants: types, hosts, battery thresholds, retry settings
  models.py   ArtifactName, Endpoint, OTAChannel, Node
  api.py      AuguryAPI (the 4 required API functions + test helpers)
robot_library.py   thin Robot keyword layer over AuguryAPI
tests/             ota.robot, dfu.robot, bad_firmware.robot
signal_processing_answers.md
```

## Design

- **OOP + encapsulation:** state is private (`_version`, ...) and exposed
  read-only via properties. A Node's version changes only through OTA
  (`poll_ota`); an Endpoint's version only through DFU (`attempt_dfu`).
  Tests cannot bypass the domain rules.
- **Single source of constants:** `config.py`.
- **`ArtifactName`:** immutable parsed artifact (`<hw>_<version>.swu`),
  case-insensitive hardware matching.
- **Fresh state per test:** the Robot library uses `scope="TEST"`.

## Domain rules

1. **OTA poll/retries:** posting to a channel does not update the Node.
   `Node.poll_ota()` is one poll cycle; `AuguryAPI.wait_for_ota()` polls up
   to 3 times with 1 s interval (configurable in `config.py`) and stops as
   soon as the expected version is reached.
2. **Artifact validation:** hardware type must match the Node
   (case-insensitive). On mismatch or malformed name the version is
   unchanged and `last_error` is set (`hardware_mismatch: ...` /
   `invalid_artifact: ...`), visible via `api_get_node_by_uuid`.
3. **DFU gating:** DFU is deferred if backlog > 0 or battery < threshold
   (EP1/EP2: 2500 mA, Canary_A: 3600 mA). Reason is stored in
   `last_dfu_status` (`deferred_backlog`, `deferred_low_battery`,
   `success`). Backlog drains via an explicit `drain_ep_backlog` action.

## Assumptions / design decisions

- Versions are integers (`33`, `34`).
- `api_post_version_to_ota_channel` returns 200 when the artifact is added
  to an existing channel, even if it will later be rejected by the Node
  (validation happens at poll time). It returns 400 for an unknown channel
  or empty artifact name. `api_clear_ota_channel` returns 400 if the
  artifact is not in the channel.
- An artifact is removed from the channel when polled, even if rejected,
  so a bad artifact cannot block the channel.
- An empty channel on poll is not an error; `last_error` is kept.
- `last_error` is cleared on a successful update.
- Battery exactly at threshold is allowed (rule is "below").
- If both backlog and battery block DFU, `backlog` is reported first.
- EP serials are generated as `<EPTYPE>-<node uuid>`.
- EP versions and Node versions are independent.

## Helpers beyond the 4 required API functions (`AuguryAPI`)

`init_node`, `ep_serial`, `tick_ota`, `wait_for_ota`, `set_ep_backlog`,
`drain_ep_backlog`, `set_ep_battery`, `offer_ep_version`, `trigger_dfu`,
`get_dfu_status`, `reset`.