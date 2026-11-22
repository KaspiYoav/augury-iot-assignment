"""Thin Robot Framework keyword layer on top of AuguryAPI."""

from robot.api.deco import keyword, library

from augury_iot.api import AuguryAPI
from augury_iot.config import OTA_MAX_RETRIES, OTA_RETRY_INTERVAL_SEC


@library(scope="TEST", auto_keywords=False)
class AuguryLibrary:
    """Each test gets a fresh library instance, so state never leaks."""

    def __init__(self):
        self._api = AuguryAPI()

    # ---------- Setup ----------
    @keyword("Init Node")
    def init_node(self, uuid, version, ep_batteries=None):
        self._api.init_node(uuid, int(version), ep_batteries)

    @keyword("Get EP Serial")
    def get_ep_serial(self, uuid, ep_type):
        return self._api.ep_serial(uuid, ep_type)

    # ---------- OTA ----------
    @keyword("Post Version To Node")
    def post_version_to_node(self, uuid, artifact):
        channel = self._api.api_get_node_by_uuid(uuid)["ota_channel"]
        return self._api.api_post_version_to_ota_channel(channel, artifact)

    @keyword("Wait For Node Version")
    def wait_for_node_version(self, uuid, expected_version,
                              retries=OTA_MAX_RETRIES,
                              interval=OTA_RETRY_INTERVAL_SEC):
        """Returns True if the node reached the version, False otherwise."""
        return self._api.wait_for_ota(
            uuid, int(expected_version), int(retries), float(interval)
        )

    @keyword("Node Version Should Be")
    def node_version_should_be(self, uuid, expected):
        actual = self._api.api_get_node_by_uuid(uuid)["version"]
        if actual != int(expected):
            raise AssertionError(
                f"Node {uuid}: expected version {expected}, got {actual}"
            )

    @keyword("Node Error Should Contain")
    def node_error_should_contain(self, uuid, text):
        err = self._api.api_get_node_by_uuid(uuid)["last_error"]
        if text not in err:
            raise AssertionError(
                f"Node {uuid}: expected error containing {text!r}, got {err!r}"
            )

    # ---------- Endpoint / DFU ----------
    @keyword("Set EP Backlog")
    def set_ep_backlog(self, serial, backlog):
        self._api.set_ep_backlog(serial, int(backlog))

    @keyword("Drain EP Backlog")
    def drain_ep_backlog(self, serial):
        self._api.drain_ep_backlog(serial)

    @keyword("Set EP Battery")
    def set_ep_battery(self, serial, battery):
        self._api.set_ep_battery(serial, int(battery))

    @keyword("Offer EP Version")
    def offer_ep_version(self, serial, version):
        self._api.offer_ep_version(serial, int(version))

    @keyword("Trigger DFU")
    def trigger_dfu(self, serial):
        return self._api.trigger_dfu(serial)

    @keyword("EP Version Should Be")
    def ep_version_should_be(self, serial, expected):
        actual = self._api.api_get_endpoint_by_serial(serial)["version"]
        if actual != int(expected):
            raise AssertionError(
                f"EP {serial}: expected version {expected}, got {actual}"
            )

    @keyword("DFU Status Should Be")
    def dfu_status_should_be(self, serial, expected):
        actual = self._api.get_dfu_status(serial)
        if actual != expected:
            raise AssertionError(
                f"EP {serial}: expected DFU status {expected!r}, got {actual!r}"
            )