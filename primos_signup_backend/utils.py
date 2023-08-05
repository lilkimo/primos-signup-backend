from re import findall

days = 'lmxjv'
num_blocks = 8
schedule_regex = fr'([{days}](?:[0-{num_blocks - 1}],)*[0-{num_blocks - 1}])'

def parse_schedule(schedule):
    parsed_schedule = ''
    for i, day in enumerate(days):
        blocks = []
        for block, availability in enumerate(schedule[i*num_blocks: i*num_blocks+num_blocks]):
            if availability:
                blocks.append(str(block))
        if len(blocks):
            parsed_schedule += f'{day}{",".join(blocks)}'
    return parsed_schedule

def unparse_schedule(parsed_schedule):
    schedule = [False]*5*num_blocks
    for day in findall(schedule_regex, parsed_schedule):
        for block in day[1:].split(','):
            schedule[days.index(day[0])*num_blocks + int(block)] = True
    return schedule
