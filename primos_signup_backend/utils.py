num_blocks = 8

def parse_schedule(schedule):
    parsed_schedule = ''
    for i, day in enumerate('lmxjv'):
        blocks = []
        for block, availability in enumerate(schedule[i*num_blocks: i*num_blocks+num_blocks]):
            if availability:
                blocks.append(str(block))
        if len(blocks):
            parsed_schedule += f'{day}{",".join(blocks)}'
    return parsed_schedule