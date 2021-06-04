from dataclasses import dataclass, field
from typing import List
from pandas import DataFrame

class triVariables:
    max_tss_weekday = 100
    max_time_weekday = 70
    max_tss_weekend = 200
    max_time_weekend = 140

    weekdays = ['Tues', 'Wed', 'Thurs', 'Fri']
    weekend = ['Sat', 'Sun']

    run_file = 'Run.xlsx'
    bike_file = 'Bike.xlsx'
    swim_file = 'Swim.xlsx'

    tss = 'TSS'
    duration = 'Duration/Distance'
    code = 'Code'
    type = 'Type'
    zone_1 = 'Zone 1'
    zone_2 = 'Zone 2'
    zone_3 = 'Zone 3'
    zone_4 = 'Zone 4'
    zone_5 = 'Zone 5'
    high_duration = 'High Duration'
    low_duration = 'Low Duration'

    target_tss = 500
    low_tgt = 0.8
    high_tgt = 0.2
    bike_tgt_percent = 0.67
    run_tgt_percent = 0.33
    swim_tgt_percent = 0.0


