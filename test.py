import pyKeithleyCtl as RC
from time import sleep

PS = RC.KeithleySupply("169.254.127.39")

PS.reset()

print(PS.IDN)

print("Access level", PS.ask(":SYSTem:ACCess?"))

print(PS.get_voltage() )
print(PS.get_ocp() )


PS.set_voltage(4.2)
PS.set_ocp(0.001)


print(1, PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )

PS.enable_output()

sleep(1)

print(2, PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )

sleep(1)

print(PS.track_current(5))

PS.disable_output()

print(3, PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )
