import numpy as np

metadata = {'apiLevel': '2.1'}
spotting_tuples=[(('A1',), ('A1',), (5,))]
soc_well='A1'

# Constants
CANDIDATE_P10_SLOTS = ['9', '2', '5']
CANDIDATE_P300_SLOTS = ['3', '6']
P10_TIPRACK_TYPE = 'opentrons_96_tiprack_300ul'
P300_TIPRACK_TYPE = 'opentrons_96_tiprack_300ul'
P10_MOUNT = 'right'
P300_MOUNT = 'left'
ASSEMBLY_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
ASSEMBLY_PLATE_SLOT = '8'
TEMPDECK_SLOT = '10'
TRANSFORMATION_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
SOC_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
SOC_PLATE_SLOT = '7'
TUBE_RACK_TYPE = 'opentrons_15_tuberack_falcon_15ml_conical'
TUBE_RACK_SLOT = '11'
SPOTTING_WASTE_WELL = 'A1'
AGAR_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
AGAR_PLATE_SLOT = '1'
TEMP = 4
ASSEMBLY_VOL = 5
MIX_SETTINGS = (4, 5)
INCUBATION_TIME = 20
SOC_VOL = 125
SOC_MIX_SETTINGS = (4, 50)
TEMP = 37
OUTGROWTH_TIME = 60
SOC_ASPIRATION_RATE = 25
P300_DEFAULT_ASPIRATION_RATE = 150

def run(protocol):
    # Tiprack slots
    p10_p300_tiprack_slots = tiprack_slots(spotting_tuples)
    p10_slots = CANDIDATE_P10_SLOTS[
        :p10_p300_tiprack_slots[0]]
    p300_slots = CANDIDATE_P300_SLOTS[
        :p10_p300_tiprack_slots[1]]

    # Define labware
    p10_tipracks = [protocol.load_labware(P10_TIPRACK_TYPE, slot)
                    for slot in p10_slots]
    p300_tipracks = [protocol.load_labware(P300_TIPRACK_TYPE, slot)
                    for slot in p300_slots]
    p10_pipette = protocol.load_instrument("p10_single",mount=P10_MOUNT, tip_racks=p10_tipracks)
    p300_pipette = protocol.load_instrument("p300_multi",mount=P300_MOUNT, tip_racks=p300_tipracks)

    assembly_plate = protocol.load_labware(ASSEMBLY_PLATE_TYPE, ASSEMBLY_PLATE_SLOT)
    tempdeck = protocol.load_module('tempdeck', TEMPDECK_SLOT)
    transformation_plate = tempdeck.load_labware(TRANSFORMATION_PLATE_TYPE,TEMPDECK_SLOT)
    soc_plate = protocol.load_labware(SOC_PLATE_TYPE, SOC_PLATE_SLOT)
    tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_SLOT)
    spotting_waste = tube_rack.wells(SPOTTING_WASTE_WELL)
    agar_plate = protocol.load_labware(AGAR_PLATE_TYPE, AGAR_PLATE_SLOT)

    # Register agar_plate for calibration
    p10_pipette.transfer(1, agar_plate.wells(
        'A1'), agar_plate.wells('H12'), trash=False)

    transformation_wells = generate_transformation_wells(spotting_tuples)
    # Set temperature deck to 4 °C and load competent cells
    tempdeck.set_temperature(TEMP)
    protocol.pause()
    protocol.comment('Load competent cells, uncap and resume run')
    # Transfer final assemblies
    p10_pipette.transfer(ASSEMBLY_VOL,
                         assembly_plate.wells()[0:len(transformation_wells)],
                         transformation_plate.wells()[0:len(transformation_wells)], new_tip='always',mix_after=(MIX_SETTINGS))

    # Incubate for 20 minutes and remove competent cells for heat shock
    p10_pipette.delay()
    protocol.pause()
    protocol.comment('Remove transformation reactions, conduct heatshock and replace.')

    protocol.pause()
    protocol.comment('Remove final assembly plate. Introduce agar tray and deep well plate containing SOC media. Resume run.')

    cols_list = []
    for spotting_tuple in spotting_tuples:
        source_wells_cols = [source_well[1:]
                             for source_well in spotting_tuple[0]]
        unique_cols = [col for i, col in enumerate(
            source_wells_cols) if source_wells_cols.index(col) == i]
        cols_list.append(unique_cols)

    spotting_tuples_cols = [col for cols in cols_list for col in cols]
    unique_cols = [col for i, col in enumerate(
        spotting_tuples_cols) if spotting_tuples_cols.index(col) == i]
        
    # Define wells
    transformation_cols = transformation_plate.columns()[0:len(unique_cols)]
    soc = soc_plate.wells(soc_well)

    # Add SOC to transformed cells
    p300_pipette.transfer(SOC_VOL, soc, transformation_cols,
                          new_tip='always', mix_after=SOC_MIX_SETTINGS)

    # Incubate for 1 hour at 37 °C
    tempdeck.set_temperature(TEMP)
    p300_pipette.delay()
    tempdeck.deactivate()

    spot_transformations(
        protocol,
        spotting_tuples,
        p10_pipette,
        spotting_waste,
        transformation_plate,
        agar_plate,
        p300_pipette)


def generate_transformation_wells(spotting_tuples):
    wells = []
    for spotting_tuple in spotting_tuples:
        for source_well in spotting_tuple[0]:
            wells.append(source_well)
    transformation_wells = [well for i, well in enumerate(
        wells) if wells.index(well) == i]
    return transformation_wells


def tiprack_slots(spotting_tuples,max_spot_vol=5):
    transformation_reactions = len(
        generate_transformation_wells(spotting_tuples))
    spotting_reactions = 0
    for spotting_tuple in spotting_tuples:
        spots = np.array(spotting_tuple[2])/max_spot_vol
        np.ceil(spots)
        spotting_reactions = spotting_reactions + int(np.sum(spots))

    # p10 tiprack slots
    p10_tips = transformation_reactions + spotting_reactions
    p10_tiprack_slots = p10_tips // 96 + 1 if p10_tips % 96 > 0 else p10_tips / 96

    # p300 tiprack slots
    p300_tips = transformation_reactions + spotting_reactions
    p300_tiprack_slots = p300_tips // 96 + \
        1 if p300_tips % 96 > 0 else p300_tips / 96
    return int(p10_tiprack_slots), int(p300_tiprack_slots)



def spot_transformations(
        protocol,
        spotting_tuples,
        p10_pipette,
        spotting_waste,
        transformation_plate,
        agar_plate,
        p300_pipette,
        dead_vol=2,
        spotting_dispense_rate=0.025,
        stabbing_depth=2,
        max_spot_vol=5):

    def spot(
            source,
            target,
            spot_vol):
        """Spots an individual reaction using the p10 pipette.

        Args:
        source (str): Well containing the transformation reaction to be spotted.
        target (str): Well transformation reaction is to be spotted to.
        spot_vol (float): Volume of transformation reaction to be spotted (uL).  

        """
        # Constants
        DEFAULT_HEAD_SPEED = {'x': 400, 'y': 400,
                              'z': 125, 'a': 125}
        SPOT_HEAD_SPEED = {'x': 400, 'y': 400, 'z': 125,
                           'a': 125 // 4}
        DISPENSING_HEIGHT = 5
        SAFE_HEIGHT = 15  # height avoids collision with agar tray.
        source = source[0]
        target = target[0]
        # Spot
        p10_pipette.pick_up_tip()
        p10_pipette.aspirate(spot_vol + dead_vol, source)
        p10_pipette.dispense(volume=spot_vol, rate=spotting_dispense_rate)

        # Dispose of dead volume and tip
        p10_pipette.dispense(dead_vol, spotting_waste[0])
        p10_pipette.blow_out()
        p10_pipette.drop_tip()

    def spot_tuple(spotting_tuple):
        """Spots all reactions defined by the spotting tuple. Requires the function spot.

            Args:
            spotting_tuple (tuple): Spotting reactions given in the form: (source wells), (target wells), (spotting volumes).

        """
        source_wells = spotting_tuple[0]
        target_wells = spotting_tuple[1]
        spot_vols = list(spotting_tuple[2])
        while max(spot_vols) > 0:
            for index, spot_vol in enumerate(spot_vols):
                if spot_vol == 0:
                    pass
                else:
                    vol = spot_vol if spot_vol <= max_spot_vol else max_spot_vol
                    spot(transformation_plate.wells(source_wells[index]),
                         agar_plate.wells(target_wells[index]), vol)
                    spot_vols[index] = spot_vols[index] - vol

    # Constants
    TRANSFORMATION_MIX_SETTINGS = [4, 50]

    # Spot transformation reactions
    for spotting_tuple in spotting_tuples:
        source_wells_cols = [source_well[1:]
                             for source_well in spotting_tuple[0]]
        unique_cols = [col for i, col in enumerate(
            source_wells_cols) if source_wells_cols.index(col) == i]
        for col in unique_cols:
            p300_pipette.pick_up_tip()
            for c in col:
                p300_pipette.mix(TRANSFORMATION_MIX_SETTINGS[0],
                                TRANSFORMATION_MIX_SETTINGS[1],
                                transformation_plate.columns(c)[0][0])
            p300_pipette.drop_tip()
        spot_tuple(spotting_tuple)
