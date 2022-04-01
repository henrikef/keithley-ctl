import pyKeithleyCtl as RC
from time import sleep

PS = RC.KeithleySupply("169.254.127.39")

PS.clear()
PS.reset()

print(PS.IDN)

print("Access level", PS.ask(":SYSTem:ACCess?"))

print(PS.get_voltage() )
print(PS.get_ocp() )


PS.set_voltage(4.2)
PS.set_ocp(0.001)


print(1, PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )


PS.enable_output()

PS.start_measurement()

sleep(5)

#print(2, PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )

sleep(1)

#print(3, PS.get_voltage(), PS.measure_voltage(), PS.measure_current() )

data, nRow = PS.stop_measurement()

PS.disable_output()

data = PS.to_csv(data, nRow)

print(data)

PS.close()
