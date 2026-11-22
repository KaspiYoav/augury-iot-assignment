from augury_iot.models import ArtifactName

a = ArtifactName.parse("moxa_34.swu")
print(a)                       # moxa_34.swu
print(a.hardware_type)         # MOXA
print(a.version)               # 34
print(a.matches("MOXA"))       # True
print(a.matches("cassia"))     # False

# case-insensitive
print(ArtifactName.parse("MOXA_34.SWU").matches("moxa"))  # True

# bad input
try:
    ArtifactName.parse("moxa34.swu")
except ValueError as e:
    print("Error:", e)