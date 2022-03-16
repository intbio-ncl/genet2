
metadata = {'apiLevel': '2.1'}
def run(protocol):
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_1])
    p300.transfer(100, plate.wells('A1'), plate.wells('B1'))
    p300.transfer(100, plate.wells('C1'), plate.wells('D1'))