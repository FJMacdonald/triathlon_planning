from dataclasses import dataclass, field
from typing import List
from pandas import DataFrame
import numpy as np


class triVariables:
    run_ftp = 295.0  # Your running FTP
    bike_ftp = 170.0  # Your bike FTP
    swim_css = 35.29  # Your Critical Swim Speed in meters/minute or yards/minute
    # If you currently have it in minutes / 100 yards (e.g. 2:50 / 100 yards)
    # The calculation to get this is 100 * 60 / # seconds

    bike_zone_power_multiplier = np.array([0.6, 0.765, 0.955, 1.06, 1.30])
    run_zone_power_multiplier = np.array([0.63, 0.82, 0.97, 1.115, 1.35])
    swim_zone_css_multiplier = np.array([0.795, 0.875, 0.98, 1.04, 1.1])

    # Score weights
    tot_weights = 6.0
    tot_tss_weight = 1.0 / tot_weights  # Overall TSS score weight
    tgt_weight = 1.0 / tot_weights  # Overall 80/20 score weight
    # rbs = run, bike, swim
    rbs_dur_split_weight = 1.0 / tot_weights  # RBS Duration 2/3-1/3 score weight
    rbs_tss_split_weight = 1.0 / tot_weights  # RBS TSS 1/3-1/3 score weight
    rbs_dur_tgt_split_weight = 1.0 / tot_weights  # RBS Duration is 80/20 score weight (i.e. 80% of
    high_zone_split_weight = 1.0 / tot_weights # Distribution of the high zone intensities (
    dist_metric_exponential = 1  # Basically how much to punish values which are far away from the target, better to have everything off by 0.1 than everything spot on and one off by 0.08


    target_tss = 500
    low_tgt = 0.8
    high_tgt = 0.2

    # Within the high zone, how much of each to prefer
    zone_3_tgt = 0.5
    zone_4_tgt = 0.25
    zone_5_tgt = 0.25

    bike_tgt_percent = 0.67
    run_tgt_percent = 0.33
    swim_tgt_percent = 0.0

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
    duration = 'Duration'
    code = 'Code'
    type = 'Type'
    zone_1 = 'Zone 1'
    zone_2 = 'Zone 2'
    zone_3 = 'Zone 3'
    zone_4 = 'Zone 4'
    zone_5 = 'Zone 5'

    intensity_factor = 'Intensity Factor'
    normalized_power = 'Normalized Power'
    high_duration_head = 'High Duration'
    low_duration_head = 'Low Duration'


class workout:
    plan = []

    total_tss = 0.0

    duration = 0.0
    high_dur = 0.0
    low_dur = 0.0
    high_pct = 0.0
    low_pct = 0.0

    # Outputs
    score = 0.0
    tss_score = 0.0
    tgt_score = 0.0
    high_dur_percent, low_dur_percent = 0.0, 0.0
    run_dur_percent, bike_dur_percent, swim_dur_percent = 0.0, 0.0, 0.0
    run_tss_percent, bike_tss_percent, swim_tss_percent = 0.0, 0.0, 0.0
    run_high_dur_percent, run_low_dur_percent = 0.0, 0.0
    bike_high_dur_percent, bike_low_dur_percent = 0.0, 0.0
    swim_high_dur_percent, swim_low_dur_percent = 0.0, 0.0
    dur_tgt_score = 0.0
    tss_tgt_score = 0.0
    dur_split_tgt_score = 0.0
    high_split_tgt_score = 0.0

    class bike:
        name = 'Bike'
        tgt_percent = 0.0

        dur = 0.0
        dur_percent = 0.0

        tss = 0.0
        tss_percent = 0.0

        high_dur = 0.0
        low_dur = 0.0
        high_dur_percent = 0.0
        low_dur_percent = 0.0

        zone_3 = 0.0
        zone_4 = 0.0
        zone_5 = 0.0
        zone_3_percent = 0.0
        zone_4_percent = 0.0
        zone_5_percent = 0.0

    class run:
        name = 'Run'
        tgt_percent = 0.0

        dur = 0.0
        dur_percent = 0.0

        tss = 0.0
        tss_percent = 0.0

        high_dur = 0.0
        low_dur = 0.0
        high_dur_percent = 0.0
        low_dur_percent = 0.0

        zone_3 = 0.0
        zone_4 = 0.0
        zone_5 = 0.0
        zone_3_percent = 0.0
        zone_4_percent = 0.0
        zone_5_percent = 0.0

    class swim:
        name = 'Swim'
        tgt_percent = 0.0

        dur = 0.0
        dur_percent = 0.0

        tss = 0.0
        tss_percent = 0.0

        high_dur = 0.0
        low_dur = 0.0
        high_dur_percent = 0.0
        low_dur_percent = 0.0

        zone_3 = 0.0
        zone_4 = 0.0
        zone_5 = 0.0
        zone_3_percent = 0.0
        zone_4_percent = 0.0
        zone_5_percent = 0.0

