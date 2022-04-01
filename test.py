import pyKeithleyCtl as RC
from time import sleep

PS = RC.KeithleySupply("169.254.127.39")

print(PS.IDN)

print("Access level", PS.ask(":SYSTem:ACCess?"))

print(PS.get_voltage() )
print(PS.get_ocp() )


PS.set_voltage(4.2)
PS.set_ocp(0.001)

print(PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )

PS.enable_output()
print(PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )

sleep(10)

PS.disble_output()

print(PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )
