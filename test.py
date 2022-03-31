import pyKeithleyCtl as RC
from time import sleep

PS = RC.KeithleySupply("169.254.55.31")

print(PS.IDN)

print(PS.get_voltage() )
print(PS.get_ocp() )

PS.set_voltage(1, 4.2)
print(PS.get_voltage() )

PS.enable_output(1)
print(PS.get_voltage() )

sleep(10 )

PS.disble_output(1)

print(PS.get_voltage() )
