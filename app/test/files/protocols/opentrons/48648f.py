import os
import json
def get_values(*names):
    import json
    _all_values = json.loads("""{"sample_count":3,"sample_volume":100,"sample_deck_slots":"7,8,4,5,1,2","wells_skipped":"A1,B1,H1,A7,B7,H7"}""")
    return [_all_values[n] for n in names]


import math
custom_labware_dir = os.path.join("test","files","custom_labware")
metadata = {
    'protocolName': 'Nucleic Acid Purification',
    'author': 'McCampbell Analytical Inc. / Alex Anderson',
    'source': 'customer provided json file: Sample Plating 90 samples.json',
    'description': '',
    'created': '1600790194465',
    'lastModified': '1611762459337',
    'category': 'None',
    'subcategory': 'None',
    'tags': 'None',
    'apiLevel': '2.9'
    }

def load_custom_labware():
    in_gen = os.path.join(custom_labware_dir,"Nest 96 Well Plate 2000 µL.json")
    with open(in_gen) as labware_file:
        nest96_def = json.load(labware_file)
    
    MTC = os.path.join(custom_labware_dir,"MTC Bio 15 Tube Rack 10000 µL.json")
    with open(MTC) as labware_file:
        tuberack_def = json.load(labware_file)
    return nest96_def,tuberack_def

def run(ctx):
    # bring in constant values from json string above
    nest96_def,tuberack_def = load_custom_labware()
    [sample_count, sample_volume, sample_deck_slots,
     wells_skipped] = get_values(  # noqa: F821
      'sample_count', 'sample_volume', 'sample_deck_slots', 'wells_skipped')

    # instrument, labware and module setup
    tips_1000 = ctx.load_labware(
        'opentrons_96_filtertiprack_1000ul', '10')

    p1000 = ctx.load_instrument(
        'p1000_single_gen2', 'left', tip_racks=[tips_1000])

    # calculate the number of sample racks
    sample_racks = math.ceil(sample_count / 15)

    [*patient_samples] = [ctx.load_labware_from_definition(tuberack_def,str(slot), plate_name) for slot, plate_name in zip(sample_deck_slots.split(","),['Patient Samples Rack ' + str(i + 1) for i in range(sample_racks)])]

    temp_deck = ctx.load_module('Temperature Module gen2', '3')
    extraction_plate = temp_deck.load_labware_from_definition(
        nest96_def, 'Extraction Plate')

    hsc = ctx.load_labware_from_definition(tuberack_def, '6', 'HSC')

    # ghost movement to recognize unused tuberack on deck
    #p1000.move_to(hsc.wells()[0].top(5))

    # reference to destination wells
    destinations = extraction_plate.wells()

    # pop skipped wells out of the destinations list
    for well in wells_skipped.split(","):
        destinations.pop(
            destinations.index(extraction_plate.wells_by_name()[well]))

    # set default aspiration and dispense rates
    p1000.flow_rate.aspirate = 137.35
    p1000.flow_rate.dispense = 137.35

    # transfer patient samples to extraction plate
    rows_transferred = 0
    for rack in patient_samples:
        for row in rack.rows():
            if rows_transferred*len(row) < sample_count:
                start_index = rows_transferred*len(row)
                stop_index = (
                  lambda dest_start_index:
                  start_index + 5 if sample_count >
                  start_index + 5 else sample_count)(start_index)
                p1000.transfer(
                 sample_volume, [
                   well for well in row[:stop_index - start_index]],
                 destinations[start_index:stop_index], new_tip='always')
                rows_transferred += 1

    # 10 minute extraction at 55 degrees followed by hold at 4 degrees
    ctx.pause("Remove Extraction Plate")
    temp_deck.set_temperature(55)
    ctx.pause("Add Working Buffer\nReturn Extraction Plate")
    ctx.delay(minutes=10, msg="Incubation at 55 Celsius")
    temp_deck.set_temperature(4)
