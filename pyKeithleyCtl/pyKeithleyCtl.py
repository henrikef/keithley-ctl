import numpy as np 
import pyvisa as visa
import yaml 
import time

VISA_RM = visa.ResourceManager('@py')
class KeithleySupply():
    
    '''Used to control a single Rigol PSU.'''
    
    
    def __init__(self, address, n_ch=1, visa_resource_manager=VISA_RM):
        resource_str = f'TCPIP0::{address:s}::INSTR'
        #resource_str = f'USB0::0x05E6::0x2450::04418791::INSTR'
        #print(f"Building {resource_str}")
        self.resource = VISA_RM.open_resource(resource_str, write_termination='\n', read_termination='\n')

        self.write = self.resource.write
        self.query = self.resource.query
        
        self.clear = self.resource.clear
        self.close = self.resource.close
        
        self.n_ch = n_ch
        
        self.voltages = np.zeros(n_ch)
        #self.currents = np.zeros(n_ch)
        
        #self.ovp = np.zeros(n_ch)
        self.ocp = np.zeros(n_ch)
        
    @property
    def IDN(self):
        return self.ask("*IDN?")
    
    
    @property
    def IDENTITY(self):
        return f"IDN: {self.IDN.split(',')[-2]} IP: {self.IP}"
        
    def ask(self, question, verbose=True):
        response = self.query(question)
        if verbose:
            print("Question: {0:s} - Response: {1:s}".format(question, str(response)))
        return response
    
    def tell(self, statement):
        return self.write(statement)
        
    def reset(self):
        return self.write("*RST")
    
    def init(self):
        return self.write("INIT")
        
    def wait(self):
        return self.write("*WAI")

    def enable_output(self):
        return self.tell(f"OUTP:STAT ON")
    
    def disable_output(self):
        return self.tell(f"OUTP:STAT OFF")
    
    def set_voltage(self, voltage):
        self.tell(f":SOURCE:FUNC VOLT")
        self.tell(f":SOURCE:VOLT {voltage}")

    def get_voltage(self):
        return self.ask(':SOURCE:VOLT?')
    
    def measure_current( self ):
        return self.ask(':MEASURE:CURRENT:DC?')
        
    def measure_voltage( self ):
        return self.ask(':MEASURE:VOLTAGE:DC?')

    def set_ocp(self, ocp):
        self.tell(f':SOURCe:VOLTage:ILIMit {ocp}')
    
    def get_ocp(self):
        return self.ask(':SOURCe:VOLTage:ILIMit?')
        
    def track_current(self, max_duration_s = 60, delay_s = 1):
        self.tell('SENS:FUNC "CURR"')
        self.tell('SENS:CURR:RANG:AUTO ON')
        self.tell(':TRACE:DELelte "testData4')
        
        buffer = int(2.0*max_duration_s/delay_s)
        
        print(f'TRACE:MAKE "testData4", {buffer}' )
        print(f':TRIGger:LOAD "LoopUntilEvent", COMM, 0, NEV, {delay_s:f}, "testData4"' )
        
        self.tell(f'TRACE:MAKE "testData4", {buffer}')
        self.tell(f':TRIGger:LOAD "LoopUntilEvent", COMM, 0, NEV, {delay_s:f}, "testData4"')
        self.init()
        #self.wait()
        #time.sleep(max_duration_s)
        self.write("*TRG")
        nRow = int(self.ask(':TRAC:ACTUAL? "testData4"') )
        nCol = 3
        result =  self.query(f':TRAC:DATA? 1, {nRow}, "testData4", SOUR, READ, REL')
        
        data=np.reshape( np.fromstring(result, sep=','), (nRow, nCol) )
        
        print(type(data))
        
        return data

class KeithleyArray():
    
    '''
    
    Used to build and deploy an array of RigolSupply objects.
    Designed to be used with configuration files: 
    
        #Supply voltages.
        #Note: Negative voltage is interpreted in software as "do not use".
        S3:
            IP: "10.10.1.53"
            NCH: 2
            CH1:
                V: -99
                OCP: 0.01
            CH2: 
                V: 3.6
                OCP: 2.0

        S2:
            IP: "10.10.1.52"
            NCH: 3
            CH1:
                V: 5.0
                OCP: 1.25
            CH2: 
                V: -99
                OCP: 0.01
            CH3:
                V: 2.4
                OCP: 3.0        
        
    '''
    
    def __init__(self, psconfig_filename):
        with open(psconfig_filename) as f:
            supply_cfg = yaml.load(f, Loader=yaml.FullLoader)

        self.supply_handlers = []
        for supply in supply_cfg:
            ps = KeithleySupply(supply_cfg[supply]['IP'], supply_cfg[supply]['NCH'])
            print(ps.IDENTITY)

            for ch in range(ps.n_ch):
                ps.tell(f":OUTP:OCP CH{ch+1},ON")
                ps.voltages[ch] = supply_cfg[supply][f"CH{ch+1}"]['V']
                ps.ocp[ch] = supply_cfg[supply][f"CH{ch+1}"]['OCP']
                if ps.voltages[ch] > 0:
                    ps.set_voltage(ch+1, ps.voltages[ch])
                    ps.set_ocp(ch+1, ps.ocp[ch])
                else:
                    ps.set_voltage(ch+1, 0)
                    ps.set_ocp(ch+1, 0.001)            


            self.supply_handlers += [ps]

        print()        
    
    def apply_to_all(self, ask=None, tell=None):
        for supply in self.supply_handlers:
            if ask is not None:
                supply.ask(ask)
            if tell is not None:
                supply.tell(tell)

    def power_cycle_all_supplies(self):
        for supply in self.supply_handlers:
            for ch in range(supply.n_ch):
                print(supply.enable_output(ch+1))
                time.sleep(1)
                print(supply.disable_output(ch+1))

    def report_status(self):
        for supply in self.supply_handlers:
            print(supply.IDENTITY)
            print(f"\tChannel\t| Status\t| V\t\t| I (A)\t\t| P (W)  ")
            channel_stats = []
            channel_out_vals = []
            for ch in range(supply.n_ch):
                stat = supply.query(f"OUTP:STAT? CH{ch+1}")
                vals = supply.query(f"MEASure:ALL? CH{ch+1}")
                vals = vals.split(',')
                vals = [float(i) for i in vals]
                print(f"\t{ch+1:7d}\t| {stat:8s}\t| {vals[0]:3.4f}\t| {vals[1]:3.4f}\t| {vals[2]:3.4f}")
            print()

    def power_up_all(self, verbose=False):
        for supply in self.supply_handlers:
            for ch in range(supply.n_ch):
                if supply.voltages[ch] > 0:
                    supply.enable_output(ch+1)        
        if verbose:
            time.sleep(1.0)
            self.report_status()


    def power_down_all(self, verbose=False):
        if verbose:
            self.report_status()
            print("----------------------")
        for supply in self.supply_handlers:
            for ch in range(supply.n_ch):
                supply.disable_output(ch+1)
        if verbose:
            time.sleep(1.0)
            self.report_status()
