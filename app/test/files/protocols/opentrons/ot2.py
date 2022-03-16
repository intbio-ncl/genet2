metadata = {'apiLevel': '2.1'}

def run(protocol):
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_1])
    mag_mod = protocol.load_module('magnetic module', 3)
    mag_plate = mag_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    tc_mod = protocol.load_module('Thermocycler Module')
    temp_plate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')

    # Digestion
    # Add restriction enzymes to modules.
    p300.transfer(100, plate['A6'], plate['B1'])
    p300.transfer(100, plate['A6'], plate['B2'])
    p300.transfer(100, plate['A6'], plate['B3'])
    # Transfer RE + Modules to magnetic plate.
    p300.transfer(100, plate['B1'], mag_plate['A1'])
    p300.transfer(100, plate['B2'], mag_plate['A2'])
    p300.transfer(100, plate['B3'], mag_plate['A3'])
    #mag_mod.engage()
    #mag_mod.disengage()

    # Assembly
    # Move payloads to from magnetic plate.
    p300.transfer(100, mag_plate['A1'], plate['C1'])
    p300.transfer(100, mag_plate['A2'], plate['C2'])
    p300.transfer(100, mag_plate['A3'], plate['C3'])
    # Transformation
    p300.transfer(100, plate['A4'], plate['D4'])
    p300.transfer(100, plate['A5'], plate['D4'])
    p300.transfer(100, plate['C1'], plate['D4'])
    p300.transfer(100, plate['C2'], plate['D4'])
    p300.transfer(100, plate['C3'], plate['D4'])
    #tc_mod.open_lid()
    p300.transfer(100, plate['D4'], temp_plate['A1'])
    #tc_mod.close_lid()
    #tc_mod.set_block_temperature(4)
    #tc_mod.open_lid()
    p300.transfer(100, temp_plate['A1'], temp_plate['E1'])



