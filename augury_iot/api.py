"""AuguryAPI: the fake cloud API. Tests talk only to this layer."""

import time
from typing import Optional

from augury_iot.config import (
    HTTP_BAD_REQUEST,
    HTTP_OK,
    OTA_MAX_RETRIES,
    OTA_RETRY_INTERVAL_SEC,
    OTA_CHANNEL_PREFIX,
)
from augury_iot.models import Endpoint, Node


class AuguryAPI:
    """In-memory registry of Nodes and Endpoints + the API functions."""

    def __init__(self):
        self._nodes: dict[str, Node] = {}
        self._endpoints: dict[str, Endpoint] = {}   # serial -> Endpoint

    def reset(self) -> None:
        """Clear everything (used in test setup/teardown)."""
        self._nodes.clear()
        self._endpoints.clear()

    # ---------- internal lookups ----------
    def _node(self, uuid: str) -> Node:
        if uuid not in self._nodes:
            raise KeyError(f"Unknown node uuid: {uuid}")
        return self._nodes[uuid]

    def _node_by_channel(self, channel: str) -> Optional[Node]:
        for node in self._nodes.values():
            if node.channel.name == channel:
                return node
        return None

    def _endpoint(self, serial: str) -> Endpoint:
        if serial not in self._endpoints:
            raise KeyError(f"Unknown endpoint serial: {serial}")
        return self._endpoints[serial]

    # ---------- the 4 required API functions ----------
    def api_get_endpoint_by_serial(self, serial_number: str) -> dict:
        return self._endpoint(serial_number).to_dict()

    def api_get_node_by_uuid(self, uuid: str) -> dict:
        return self._node(uuid).to_dict()

    def api_post_version_to_ota_channel(self, ota_channel: str,
                                        version_artifact: str) -> int:
        node = self._node_by_channel(ota_channel)
        if node is None:
            return HTTP_BAD_REQUEST
        return HTTP_OK if node.channel.post(version_artifact) else HTTP_BAD_REQUEST

    def api_clear_ota_channel(self, ota_channel: str,
                              version_artifact: str) -> int:
        node = self._node_by_channel(ota_channel)
        if node is None:
            return HTTP_BAD_REQUEST
        return HTTP_OK if node.channel.clear(version_artifact) else HTTP_BAD_REQUEST

    # ---------- helpers for tests ----------
    def init_node(self, uuid: str, version: int,
                  ep_batteries: Optional[dict] = None) -> dict:
        """Create a Node with 3 paired EPs (EP1, EP2, CANARY_A).

        Serials are generated as '<EPTYPE>-<uuid>'.
        ep_batteries optionally overrides battery per EP type.
        """
        batteries = {"EP1": 3000, "EP2": 3000, "CANARY_A": 4000}
        batteries.update({k.upper(): v for k, v in (ep_batteries or {}).items()})

        eps = [
            Endpoint(f"{t}-{uuid}", t, uuid, battery=batteries[t], version=1)
            for t in ("EP1", "EP2", "CANARY_A")
        ]
        node = Node(uuid, version, eps)
        self._nodes[uuid] = node
        for ep in eps:
            self._endpoints[ep.serial] = ep
        return node.to_dict()

    def ep_serial(self, uuid: str, ep_type: str) -> str:
        return f"{ep_type.upper()}-{uuid}"

    def tick_ota(self, uuid: str) -> bool:
        """One OTA poll cycle on the node."""
        return self._node(uuid).poll_ota()

    def wait_for_ota(self, uuid: str, expected_version: int,
                     retries: int = OTA_MAX_RETRIES,
                     interval: float = OTA_RETRY_INTERVAL_SEC) -> bool:
        """Poll up to `retries` times. True as soon as version == expected."""
        node = self._node(uuid)
        for attempt in range(retries):
            node.poll_ota()
            if node.version == expected_version:
                return True
            if attempt < retries - 1:
                time.sleep(interval)
        return False

    def set_ep_backlog(self, serial: str, backlog: int) -> None:
        self._endpoint(serial).set_backlog(backlog)

    def drain_ep_backlog(self, serial: str) -> None:
        self._endpoint(serial).drain_backlog()

    def set_ep_battery(self, serial: str, battery: int) -> None:
        self._endpoint(serial).set_battery(battery)

    def offer_ep_version(self, serial: str, version: int) -> None:
        self._endpoint(serial).offer_version(version)

    def trigger_dfu(self, serial: str) -> bool:
        return self._endpoint(serial).attempt_dfu()

    def get_dfu_status(self, serial: str) -> str:
        return self._endpoint(serial).last_dfu_status