metadata = {'apiLevel': '2.1'}
sample_number=3
ethanol_well='A11'
def run(protocol):
    magbead(protocol,sample_number=sample_number,
            ethanol_well=ethanol_well, elution_buffer_well='A1')
            
def magbead(
        protocol,
        sample_number,
        ethanol_well,
        elution_buffer_well,
        sample_volume=30,
        bead_ratio=1.8,
        elution_buffer_volume=40,
        sample_offset=0,
        tiprack_type="opentrons_96_tiprack_300ul"):
    """Implements magbead purification reactions for BASIC assembly using an opentrons OT-2.

    Selected args:
        ethanol_well (str): well in reagent container containing ethanol.
        elution_buffer_well (str): well in reagent container containing elution buffer.
        sample_offset (int): offset the intial sample column by the specified value.

    """

    # Constants
    TIPS_PER_SAMPLE = 9
    CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9', '2', '5']
    MAGDECK_POSITION = '1'
    MIX_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
    MIX_PLATE_POSITION = '4'
    REAGENT_CONTAINER_TYPE = 'nest_12_reservoir_15ml'
    REAGENT_CONTAINER_POSITION = '7'
    BEAD_CONTAINER_TYPE = 'geb_96_tiprack_1000ul'
    BEAD_CONTAINER_POSITION = '8'
    LIQUID_WASTE_WELL = 'A12'
    BEADS_WELL = 'A1'
    DEAD_TOTAL_VOL = 5
    IMMOBILISE_MIX_REPS = 10
    MAGDECK_HEIGHT = 20
    AIR_VOL_COEFF = 0.1
    ETHANOL_VOL = 150
    ETHANOL_DEAD_VOL = 50
    ELUTION_MIX_REPS = 20
    ELUTION_DEAD_VOL = 2

    # Errors
    if sample_number > 48:
        raise ValueError('sample number cannot exceed 48')

    # Tips and pipette
    total_tips = sample_number * TIPS_PER_SAMPLE
    tiprack_num = total_tips // 96 + (1 if total_tips % 96 > 0 else 0)
    slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
    tipracks = [protocol.load_labware(tiprack_type, slot)
                for slot in slots]
    pipette = protocol.load_instrument(
        "p300_multi",
        mount="left",
        tip_racks=tipracks)

    # Define labware
    MAGDECK = protocol.load_module('magdeck', MAGDECK_POSITION)
    MAGDECK.disengage()
    mag_plate = MAGDECK.load_labware(MIX_PLATE_TYPE, MAGDECK_POSITION)
    mix_plate = protocol.load_labware(MIX_PLATE_TYPE, MIX_PLATE_POSITION)
    reagent_container = protocol.load_labware(
        REAGENT_CONTAINER_TYPE, REAGENT_CONTAINER_POSITION)
    bead_container = protocol.load_labware(BEAD_CONTAINER_TYPE, BEAD_CONTAINER_POSITION)
    col_num = sample_number // 8 + (1 if sample_number % 8 > 0 else 0)
    samples = [col for col in mag_plate.columns()[0 + sample_offset:col_num + sample_offset]]
    output = [col for col in mag_plate.columns()[6 + sample_offset:col_num + 6 + sample_offset]]
    mixing = [col for col in mix_plate.columns()[0 + sample_offset:col_num + sample_offset]]

    # Define reagents and liquid waste
    liquid_waste = reagent_container.wells(LIQUID_WASTE_WELL)
    beads = bead_container.wells(BEADS_WELL)
    ethanol = reagent_container.wells(ethanol_well)
    elution_buffer = reagent_container.wells(elution_buffer_well)

    # Define bead and mix volume
    bead_volume = sample_volume * bead_ratio
    if bead_volume / 2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = bead_volume / 2
    total_vol = bead_volume + sample_volume + DEAD_TOTAL_VOL

    # Mix beads and PCR samples and incubate
    for target in range(int(len(samples))):
        # Aspirate beads
        pipette.pick_up_tip()
        pipette.aspirate(bead_volume, beads[0])

        # Transfer and mix on  
        for s in samples[target]:
            for m in mixing[target]:
                pipette.aspirate(sample_volume + DEAD_TOTAL_VOL, s)
                pipette.dispense(total_vol, m)
                pipette.mix(IMMOBILISE_MIX_REPS, mix_vol, m)
                pipette.blow_out()

        # Dispose of tip
        pipette.drop_tip()

    # Immobilise sample
    pipette.delay()

    # Transfer sample back to magdeck
    for target in range(int(len(samples))):
        pipette.transfer(total_vol, mixing[target], samples[target],
                         blow_out=True)

    # Engagae MagDeck and incubate
    MAGDECK.engage(height=MAGDECK_HEIGHT)
    pipette.delay()

    # Remove supernatant from magnetic beads
    for target in samples:
        pipette.transfer(total_vol, target, liquid_waste, blow_out=True)

    # Wash beads twice with 70% ethanol
    air_vol = pipette.max_volume * AIR_VOL_COEFF
    for cycle in range(2):
        for target in samples:
            pipette.transfer(ETHANOL_VOL, ethanol, target, air_gap=air_vol)
        pipette.delay()
        for target in samples:
            pipette.transfer(ETHANOL_VOL + ETHANOL_DEAD_VOL, target, liquid_waste,
                             air_gap=air_vol)

    # Dry at RT
    pipette.delay()

    # Disengage MagDeck
    MAGDECK.disengage()

    # Mix beads with elution buffer
    if elution_buffer_volume / 2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = elution_buffer_volume / 2
    for target in samples:
        pipette.transfer(elution_buffer_volume, elution_buffer,
                         target, mix_after=(ELUTION_MIX_REPS, mix_vol))

    # Incubate at RT for "elution_time" minutes
    pipette.delay()

    # Engagae MagDeck for 1 minute and remain engaged for DNA elution
    MAGDECK.engage(height=MAGDECK_HEIGHT)
    pipette.delay()

    # Transfer clean PCR product to a new well
    for target, dest in zip(samples, output):
        pipette.transfer(elution_buffer_volume - ELUTION_DEAD_VOL, target,
                         dest, blow_out=False)

    # Disengage MagDeck
    MAGDECK.disengage()