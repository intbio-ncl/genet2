import numpy as np

final_assembly_dict={"A1": ["A7", "B7", "C7"]}
tiprack_num=1
metadata = {'apiLevel': '2.1'}
def run(protocol):
    final_assembly(protocol,final_assembly_dict=final_assembly_dict,
                    tiprack_num=tiprack_num)


def final_assembly(protocol,final_assembly_dict, tiprack_num, tiprack_type="geb_96_tiprack_1000ul"):
    # Constants
    CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9', '2', '5', '8', '11']
    PIPETTE_MOUNT = 'right'
    MAG_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
    MAG_PLATE_POSITION = '1'
    TUBE_RACK_TYPE = 'opentrons_15_tuberack_falcon_15ml_conical'
    TUBE_RACK_POSITION = '7'
    DESTINATION_PLATE_TYPE = 'opentrons_96_aluminumblock_nest_wellplate_100ul'
    TEMPDECK_SLOT = '4'
    TEMP = 20
    TOTAL_VOL = 15
    PART_VOL = 1.5
    MIX_SETTINGS = (1, 3)

    # Errors
    sample_number = len(final_assembly_dict.keys())
    if sample_number > 96:
        raise ValueError('Final assembly nummber cannot exceed 96.')

    # Tips and pipette
    slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
    tipracks = [protocol.load_labware(tiprack_type, slot)
                for slot in slots]
    pipette = protocol.load_instrument("p10_single",mount=PIPETTE_MOUNT, tip_racks=tipracks)

    # Define Labware and set temperature
    magbead_plate = protocol.load_labware(MAG_PLATE_TYPE, MAG_PLATE_POSITION)
    tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
    tempdeck = protocol.load_module('tempdeck', TEMPDECK_SLOT)
    destination_plate= tempdeck.load_labware(DESTINATION_PLATE_TYPE, TEMPDECK_SLOT)
    tempdeck.set_temperature(TEMP)

    # Master mix transfers
    final_assembly_lens = []
    for values in final_assembly_dict.values():
        final_assembly_lens.append(len(values))
    unique_assemblies_lens = list(set(final_assembly_lens))
    master_mix_well_letters = ['A', 'B', 'C', 'D']
    for x in unique_assemblies_lens:
        master_mix_well = master_mix_well_letters[(x - 1) // 6] + str(x - 1)
        destination_inds = [i for i, lens in enumerate(
            final_assembly_lens) if lens == x]
        destination_wells = np.array(
            [key for key, value in list(final_assembly_dict.items())])
        destination_wells = list(destination_wells[destination_inds])
        pipette.pick_up_tip()
        pipette.transfer(TOTAL_VOL - x * PART_VOL, tube_rack.wells(master_mix_well),destination_plate.wells(destination_wells[0]),new_tip='never')
        pipette.drop_tip()

    # Part transfers
    for key, values in list(final_assembly_dict.items()):
        pipette.transfer(PART_VOL, magbead_plate.wells()[0:len(values)-1],
                         destination_plate.wells(key), mix_after=MIX_SETTINGS,
                         new_tip='always')

    tempdeck.deactivate()

