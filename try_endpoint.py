from augury_iot.models import Endpoint

ep = Endpoint("EP1-001", "ep1", "MOXA_TBCDB1045001", battery=3000, version=1, backlog=5)
ep.offer_version(2)

print(ep.attempt_dfu(), ep.version, ep.last_dfu_status)
# False 1 deferred_backlog

ep.drain_backlog()
print(ep.attempt_dfu(), ep.version, ep.last_dfu_status)
# True 2 success

# low battery case
ep2 = Endpoint("EP1-002", "EP1", "MOXA_TBCDB1045001", battery=2000, version=1)
ep2.offer_version(2)
print(ep2.attempt_dfu(), ep2.version, ep2.last_dfu_status)
# False 1 deferred_low_battery

# edge case: exactly at threshold is allowed
ep3 = Endpoint("EP1-003", "EP1", "MOXA_TBCDB1045001", battery=2500, version=1)
ep3.offer_version(2)
print(ep3.attempt_dfu(), ep3.version)
# True 2

# Canary_A has a higher threshold
ep4 = Endpoint("CAN-001", "canary_a", "MOXA_TBCDB1045001", battery=3000, version=1)
ep4.offer_version(2)
print(ep4.attempt_dfu(), ep4.last_dfu_status)
# False deferred_low_battery