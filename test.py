import pyKeithleyCtl as RC

PS = RC.KeithleySupply("169.254.55.31")

print(PS.IDN)
