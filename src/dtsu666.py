

class meter:
    
    def __init__(self, client, sun2000):
        self._client = client
        self._sun2000 = sun2000
        
    def updateRegisters(self):
        s2k = self._sun2000
        sladdr = 1
        
        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+8192, register_quantity=10)
        if len(regs) == 10:
            
            s2k.set_register(s2k.PHASE1_MIN_PHASE2_VOLTAGE, regs[0]/10)
            s2k.set_register(s2k.PHASE2_MIN_PHASE3_VOLTAGE, regs[1]/10)
            s2k.set_register(s2k.PHASE3_MIN_PHASE1_VOLTAGE, regs[2]/10)          
            
            s2k.set_register(s2k.PHASE1_VOLTAGE_VOLT, regs[3]/10)
            s2k.set_register(s2k.PHASE2_VOLTAGE_VOLT, regs[4]/10)
            s2k.set_register(s2k.PHASE3_VOLTAGE_VOLT, regs[5]/10)
  
            s2k.set_register(s2k.PHASE1_CURRENT_AMP, regs[6]/1000)
            s2k.set_register(s2k.PHASE2_CURRENT_AMP, regs[7]/1000)
            s2k.set_register(s2k.PHASE3_CURRENT_AMP, regs[8]/1000)
            
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KW, regs[9]/10)

        else:
            raise OSError('Could not get Data Phase 1')
        
        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+8212, register_quantity=15)
        if len(regs) == 15:
            
            s2k.set_register(s2k.PHASE1_POWER_KW, regs[0]/10)
            s2k.set_register(s2k.PHASE2_POWER_KW, regs[1]/10)
            s2k.set_register(s2k.PHASE3_POWER_KW, regs[2]/10)
            
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KVOLTAMPSREACTIVE, regs[3]/10)
            
            s2k.set_register(s2k.PHASE1_POWER_KVOLTAMPSREACTIVE, regs[4]/10)
            s2k.set_register(s2k.PHASE2_POWER_KVOLTAMPSREACTIVE, regs[5]/10)
            s2k.set_register(s2k.PHASE3_POWER_KVOLTAMPSREACTIVE, regs[6]/10)
            
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KVOLTAMPS, regs[7]/10)
            
            s2k.set_register(s2k.PHASE1_POWER_KVOLTAMPS, regs[8]/10)
            s2k.set_register(s2k.PHASE2_POWER_KVOLTAMPS, regs[9]/10)
            s2k.set_register(s2k.PHASE3_POWER_KVOLTAMPS, regs[10]/10)
            
            s2k.set_register(s2k.TOTALSYSTEM_PF, regs[11]/1000)

            s2k.set_register(s2k.PHASE1_PF, regs[12]/1000)
            s2k.set_register(s2k.PHASE2_PF, regs[13]/1000)
            s2k.set_register(s2k.PHASE3_PF, regs[14]/1000)
       
        else:
            raise OSError('Could not get Data Phase 2')
    
        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+8244, register_quantity=3)
        if len(regs) == 3:
            
            s2k.set_register(s2k.TOTAL_PHASE1_ENERGY_KWH, regs[0])
            s2k.set_register(s2k.TOTAL_PHASE2_ENERGY_KWH, regs[1])
            s2k.set_register(s2k.TOTAL_PHASE3_ENERGY_KWH, regs[2])

        else:
            raise OSError('Could not get Data Phase 3')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+8260, register_quantity=1)
        if len(regs) == 1:
            s2k.set_register(s2k.FREQUENCY_HZ, regs[0]/100)

        else:
            raise OSError('Could not get Data Phase 4')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+8272, register_quantity=1)
        if len(regs) == 1:

            s2k.set_register(s2k.TOTAL_SYSTEM_ENERGY_KWH, regs[0])

        else:
            raise OSError('Could not get Data Phase 5')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+16414, register_quantity=1)
        if len(regs) == 1:
            
            s2k.set_register(s2k.TOTALIMPORT_KWH, regs[0])
            
        else:
            raise OSError('Could not get Data Phase 6')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001+16424, register_quantity=1)
        if len(regs) == 1:
            
            s2k.set_register(s2k.TOTALEXPORT_KWH, regs[0])
            
        else:
            raise OSError('Could not get Data Phase 7')    
