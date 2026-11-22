from augury_iot.models import Node, Endpoint

uuid = "MOXA_TBCDB1045001"
eps = [
    Endpoint("EP1-001", "EP1", uuid, battery=3000, version=1),
    Endpoint("EP2-001", "EP2", uuid, battery=3000, version=1),
    Endpoint("CAN-001", "CANARY_A", uuid, battery=4000, version=1),
]
node = Node(uuid, version=33, endpoints=eps)

print(node.channel.name, node.api_host)
# OTA_MOXA_TBCDB1045001 moxa_api.azure

# happy flow
node.channel.post("moxa_34.swu")
print(node.poll_ota(), node.version, repr(node.last_error))
# True 34 ''

# bad firmware: wrong hardware type
bad = Node("CASSIA_ABC123", version=33, endpoints=[])
bad.channel.post("moxa_34.swu")
print(bad.poll_ota(), bad.version)
print(bad.last_error)
# False 33
# hardware_mismatch: node=CASSIA artifact=MOXA

# case-insensitive: uppercase artifact on lowercase-ish match
n2 = Node("MOXA_X1", version=1, endpoints=[])
n2.channel.post("MOXA_5.swu")
print(n2.poll_ota(), n2.version)
# True 5

# empty channel
print(node.poll_ota(), node.version)
# False 34

# bad node uuid
try:
    Node("FOO_123", version=1, endpoints=[])
except ValueError as e:
    print("Error:", e)