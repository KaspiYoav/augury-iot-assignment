"""Domain model: ArtifactName, Endpoint, OTAChannel, Node."""

from dataclasses import dataclass
from typing import Optional

from augury_iot.config import (
    API_HOSTS,
    ARTIFACT_EXTENSION,
    BATTERY_THRESHOLDS_MA,
    EP_TYPES,
    NODE_TYPES,
    OTA_CHANNEL_PREFIX,
)
@dataclass(frozen=True)
class ArtifactName:
    """A parsed firmware artifact name, e.g. 'moxa_34.swu'.

    Immutable: once created it cannot be changed.
    """

    hardware_type: str   # normalized to UPPERCASE, e.g. "MOXA"
    version: int         # e.g. 34

    @classmethod
    def parse(cls, raw: str) -> "ArtifactName":
        """Build an ArtifactName from a string like 'moxa_34.swu'.

        Raises ValueError if the format is invalid.
        """
        if not isinstance(raw, str) or not raw.lower().endswith(ARTIFACT_EXTENSION):
            raise ValueError(f"Artifact must end with '{ARTIFACT_EXTENSION}': {raw!r}")

        stem = raw[: -len(ARTIFACT_EXTENSION)]          # "moxa_34"
        hw_type, sep, version_str = stem.rpartition("_")  # split on LAST "_"

        if not sep or not hw_type or not version_str.isdigit():
            raise ValueError(f"Artifact must look like '<hw>_<version>.swu': {raw!r}")

        return cls(hardware_type=hw_type.upper(), version=int(version_str))

    def matches(self, node_hardware_type: str) -> bool:
        """Case-insensitive comparison with a Node's hardware type."""
        return self.hardware_type == node_hardware_type.upper()

    def __str__(self) -> str:
        return f"{self.hardware_type.lower()}_{self.version}{ARTIFACT_EXTENSION}"

class Endpoint:
    """A sensor (EP1 / EP2 / Canary_A) that gets firmware updates via DFU."""

    def __init__(self, serial: str, hardware_type: str, node_uuid: str,
                 battery: int, version: int, backlog: int = 0):
        hw = hardware_type.upper()
        if hw not in EP_TYPES:
            raise ValueError(f"Unknown endpoint type: {hardware_type!r}")

        self._serial = serial
        self._hardware_type = hw
        self._node_uuid = node_uuid
        self._battery = battery
        self._version = version
        self._backlog = backlog
        self._available_version: Optional[int] = None
        self._last_dfu_status = "idle"

    # ---------- read-only properties (encapsulation) ----------
    @property
    def serial(self) -> str:
        return self._serial

    @property
    def hardware_type(self) -> str:
        return self._hardware_type

    @property
    def node_uuid(self) -> str:
        return self._node_uuid

    @property
    def battery(self) -> int:
        return self._battery

    @property
    def version(self) -> int:
        return self._version

    @property
    def backlog(self) -> int:
        return self._backlog

    @property
    def available_version(self) -> Optional[int]:
        return self._available_version

    @property
    def last_dfu_status(self) -> str:
        return self._last_dfu_status

    @property
    def battery_threshold(self) -> int:
        return BATTERY_THRESHOLDS_MA[self._hardware_type]

    # ---------- actions that change state ----------
    def set_battery(self, battery: int) -> None:
        self._battery = battery

    def set_backlog(self, backlog: int) -> None:
        if backlog < 0:
            raise ValueError("backlog cannot be negative")
        self._backlog = backlog

    def drain_backlog(self) -> None:
        """Simulate uploading all pending samples."""
        self._backlog = 0

    def offer_version(self, version: int) -> None:
        """A new firmware version becomes available for this EP."""
        self._available_version = version

    # ---------- DFU gating (domain rule 3) ----------
    def _blocked_reason(self) -> Optional[str]:
        """Return why DFU is blocked, or None if it may proceed."""
        if self._backlog > 0:
            return "backlog"
        if self._battery < self.battery_threshold:
            return "low_battery"
        return None

    def can_dfu(self) -> bool:
        return (
            self._available_version is not None
            and self._available_version != self._version
            and self._blocked_reason() is None
        )

    def attempt_dfu(self) -> bool:
        """Try to update. Returns True if the version changed."""
        if self._available_version is None or self._available_version == self._version:
            self._last_dfu_status = "no_update_available"
            return False

        reason = self._blocked_reason()
        if reason is not None:
            self._last_dfu_status = f"deferred_{reason}"
            return False

        self._version = self._available_version
        self._last_dfu_status = "success"
        return True

    def to_dict(self) -> dict:
        return {
            "serial_number": self._serial,
            "battery": self._battery,
            "hardware_type": self._hardware_type,
            "uuid": self._node_uuid,
            "version": self._version,
            "backlog": self._backlog,
        }
class OTAChannel:
    """A queue of firmware artifacts waiting for a Node to pick them up."""

    def __init__(self, node_uuid: str):
        self._name = f"{OTA_CHANNEL_PREFIX}{node_uuid}"
        self._artifacts: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def artifacts(self) -> list[str]:
        return list(self._artifacts)  # a copy, so callers can't modify ours

    def post(self, artifact: str) -> bool:
        """Add an artifact. Returns False if the name is empty/invalid."""
        if not isinstance(artifact, str) or not artifact.strip():
            return False
        self._artifacts.append(artifact)
        return True

    def clear(self, artifact: str) -> bool:
        """Remove an artifact. Returns False if it was not in the channel."""
        if artifact not in self._artifacts:
            return False
        self._artifacts.remove(artifact)
        return True

    def pop_next(self) -> Optional[str]:
        """Take the oldest artifact (FIFO), or None if the channel is empty."""
        if not self._artifacts:
            return None
        return self._artifacts.pop(0)

class Node:
    """A gateway (AHN2 / Cassia / Moxa) that receives OTA updates."""

    def __init__(self, uuid: str, version: int, endpoints: list[Endpoint]):
        hw, sep, rest = uuid.partition("_")
        if not sep or not rest or hw.upper() not in NODE_TYPES:
            raise ValueError(f"Invalid node UUID: {uuid!r}")

        self._uuid = uuid
        self._hardware_type = hw.upper()
        self._version = version
        self._channel = OTAChannel(uuid)
        self._endpoints = {ep.serial: ep for ep in endpoints}
        self._last_error = ""

    # ---------- read-only properties ----------
    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def hardware_type(self) -> str:
        return self._hardware_type

    @property
    def version(self) -> int:
        return self._version

    @property
    def channel(self) -> OTAChannel:
        return self._channel

    @property
    def last_error(self) -> str:
        return self._last_error

    @property
    def api_host(self) -> str:
        return API_HOSTS[self._hardware_type]

    @property
    def endpoints(self) -> list[Endpoint]:
        return list(self._endpoints.values())

    # ---------- OTA: one poll cycle ----------
    def poll_ota(self) -> bool:
        """One poll: take the next artifact and try to apply it.

        Returns True if the version was updated, False otherwise.
        On failure, version is unchanged and last_error is set.
        """
        raw = self._channel.pop_next()
        if raw is None:
            return False  # nothing waiting; not an error

        try:
            artifact = ArtifactName.parse(raw)
        except ValueError as exc:
            self._last_error = f"invalid_artifact: {exc}"
            return False

        if not artifact.matches(self._hardware_type):
            self._last_error = (
                f"hardware_mismatch: node={self._hardware_type} "
                f"artifact={artifact.hardware_type}"
            )
            return False

        self._version = artifact.version
        self._last_error = ""
        return True

    def get_endpoint(self, serial: str) -> Optional[Endpoint]:
        return self._endpoints.get(serial)

    def to_dict(self) -> dict:
        return {
            "uuid": self._uuid,
            "ota_channel": self._channel.name,
            "version": self._version,
            "endpoints": list(self._endpoints.keys()),
            "last_error": self._last_error,
        }