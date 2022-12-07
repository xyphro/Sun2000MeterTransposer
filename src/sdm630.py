

class meter:
    
    def __init__(self, client, sun2000):
        self._client = client
        self._sun2000 = sun2000
        
    def updateRegisters(self):
        s2k = self._sun2000
        sladdr = 1
        
        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30001, register_quantity=36)
        if len(regs) == 36:
            s2k.set_register(s2k.PHASE1_VOLTAGE_VOLT, regs[0])
            s2k.set_register(s2k.PHASE2_VOLTAGE_VOLT, regs[1])
            s2k.set_register(s2k.PHASE3_VOLTAGE_VOLT, regs[2])
            
            s2k.set_register(s2k.PHASE1_CURRENT_AMP, regs[3])
            s2k.set_register(s2k.PHASE2_CURRENT_AMP, regs[4])
            s2k.set_register(s2k.PHASE3_CURRENT_AMP, regs[5])
            
            s2k.set_register(s2k.PHASE1_POWER_KW, regs[6]/1)
            s2k.set_register(s2k.PHASE2_POWER_KW, regs[7]/1)
            s2k.set_register(s2k.PHASE3_POWER_KW, regs[8]/1)
            
            s2k.set_register(s2k.PHASE1_POWER_KVOLTAMPS, regs[9]/1)
            s2k.set_register(s2k.PHASE2_POWER_KVOLTAMPS, regs[10]/1)
            s2k.set_register(s2k.PHASE3_POWER_KVOLTAMPS, regs[11]/1)
            
            s2k.set_register(s2k.PHASE1_POWER_KVOLTAMPSREACTIVE, regs[12]/1)
            s2k.set_register(s2k.PHASE2_POWER_KVOLTAMPSREACTIVE, regs[13]/1)
            s2k.set_register(s2k.PHASE3_POWER_KVOLTAMPSREACTIVE, regs[14]/1)

            s2k.set_register(s2k.PHASE1_PF, regs[15])
            s2k.set_register(s2k.PHASE2_PF, regs[16])
            s2k.set_register(s2k.PHASE3_PF, regs[17])
        else:
            raise OSError('Could not get Data Phase 1')

            
        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30053, register_quantity=6)
        if len(regs) == 6:
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KW, regs[0]/1)
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KVOLTAMPS, regs[2]/1)
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KVOLTAMPSREACTIVE, regs[4]/1)
            s2k.set_register(s2k.TOTALSYSTEM_PF, regs[5])
        else:
            raise OSError('Could not get Data Phase 2')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30071, register_quantity=3)
        if len(regs) == 3:
            s2k.set_register(s2k.FREQUENCY_HZ, regs[0])
            s2k.set_register(s2k.TOTALIMPORT_KWH, regs[1])
            s2k.set_register(s2k.TOTALEXPORT_KWH, regs[2])
        else:
            raise OSError('Could not get Data Phase 3')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30201, register_quantity=3)
        if len(regs) == 3:
            s2k.set_register(s2k.PHASE1_MIN_PHASE2_VOLTAGE, regs[0])
            s2k.set_register(s2k.PHASE2_MIN_PHASE3_VOLTAGE, regs[1])
            s2k.set_register(s2k.PHASE3_MIN_PHASE1_VOLTAGE, regs[2])
        else:
            raise OSError('Could not get Data Phase 4')

        # Read meter registers:
        regs = self._client.read_input_registers(slave_addr = sladdr, starting_address = 30343, register_quantity=11)
        if len(regs) == 11:
            s2k.set_register(s2k.TOTAL_SYSTEM_ENERGY_KWH, regs[0])
            s2k.set_register(s2k.TOTAL_PHASE1_ENERGY_KWH, regs[8])
            s2k.set_register(s2k.TOTAL_PHASE2_ENERGY_KWH, regs[9])
            s2k.set_register(s2k.TOTAL_PHASE3_ENERGY_KWH, regs[10])
        else:
            raise OSError('Could not get Data Phase 5')

    