from augury_iot.api import AuguryAPI

api = AuguryAPI()
uuid = "MOXA_TBCDB1045001"
api.init_node(uuid, version=33)

node = api.api_get_node_by_uuid(uuid)
print(node["version"], node["ota_channel"], node["endpoints"])
# 33 OTA_MOXA_TBCDB1045001 ['EP1-MOXA_TBCDB1045001', 'EP2-MOXA_TBCDB1045001', 'CANARY_A-MOXA_TBCDB1045001']

# OTA happy flow
print(api.api_post_version_to_ota_channel(node["ota_channel"], "moxa_34.swu"))  # 200
print(api.wait_for_ota(uuid, 34, retries=3, interval=0.1))                    # True
print(api.api_get_node_by_uuid(uuid)["version"])                              # 34

# post to unknown channel
print(api.api_post_version_to_ota_channel("OTA_NOPE", "moxa_35.swu"))         # 400

# bad firmware
api.init_node("CASSIA_ABC123", version=33)
api.api_post_version_to_ota_channel("OTA_CASSIA_ABC123", "moxa_34.swu")
print(api.wait_for_ota("CASSIA_ABC123", 34, retries=3, interval=0.1))         # False
n = api.api_get_node_by_uuid("CASSIA_ABC123")
print(n["version"], n["last_error"])
# 33 hardware_mismatch: node=CASSIA artifact=MOXA

# DFU through the API
s = api.ep_serial(uuid, "EP1")
api.set_ep_backlog(s, 5)
api.offer_ep_version(s, 2)
print(api.trigger_dfu(s), api.get_dfu_status(s))   # False deferred_backlog
api.drain_ep_backlog(s)
print(api.trigger_dfu(s), api.api_get_endpoint_by_serial(s)["version"])  # True 2