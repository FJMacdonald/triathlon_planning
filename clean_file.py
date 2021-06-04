import pandas as pd
import re
import numpy as np


# Modified/Copied from https://github.com/mtraver/python-fitanalysis/blob/master/fitanalysis/activity.py
def training_stress(zone_times, zone_multipliers, ftp):
    """Calculates the training stress of the activity.
    This is essentially a power-based version of Banister's heart rate-based
    TRIMP (training impulse). Andrew Coggan's introduction of TSS and IF
    specifies that average power should be used to calculate training stress
    (Coggan, 2003), but a later post on TrainingPeaks' blog specifies that
    normalized power should be used (Friel, 2009). Normalized power is used
    here because it yields values in line with the numbers from TrainingPeaks;
    using average power does not.

    Intensity factor is defined as the ratio of normalized power to FTP.
    See (Coggan, 2016) cited in README for more details.


    Normalized power is based on a 30-second moving average of power. Coggan's
    algorithm specifies that the moving average should start at the 30 second
    point in the data, but this implementation does not (it starts with the
    first value, like a standard moving average). This is an acceptable
    approximation because normalized power shouldn't be relied upon for efforts
    less than 20 minutes long (Coggan, 2012), so how the first 30 seconds are
    handled doesn't make much difference. Also, the values computed by this
    implementation are very similar to those computed by TrainingPeaks, so
    changing the moving average implementation doesn't seem to be critical.
    This function also does not specially handle gaps in the data. When a pause
    is present in the data (either from autopause on the recording device or
    removal of stopped periods in post-processing) the timestamp may jump by a
    large amount from one sample to the next. Ideally this should be handled in
    some way that takes into account the physiological impact of that rest, but
    currently this algorithm does not. But again, the values computed by this
    implementation are very similar to those computed by TrainingPeaks, so
    changing gap handling doesn't seem to be critical.
    See (Coggan, 2003) cited in README for details on the rationale behind the
    calculation.

    Args:
      ftp: Functional threshold power in Watts.
    Returns:
      Training stress as a float
    """

    norm_power = np.sqrt(np.sqrt(np.sum(np.multiply((ftp * zone_multipliers) ** 4, zone_times)) / np.sum(zone_times)))
    intensity = norm_power / float(ftp)
    total_time = np.sum(zone_times) / 60.0
    tss = 100 * (intensity ** 2) * total_time

    return norm_power, intensity, tss


zone_1 = 'Zone 1'
zone_2 = 'Zone 2'
zone_3 = 'Zone 3'
zone_4 = 'Zone 4'
zone_5 = 'Zone 5'
tss = 'TSS'
intensity_factor = 'Intensity Factor'
normalized_power = 'Normalized Power'
high_duration_head = 'High Duration'
low_duration_head = 'Low Duration'

run_ftp = 295.0
bike_ftp = 170.0

bike_zone_power_multiplier = np.array([0.6, 0.765, 0.955, 1.06, 1.30])
run_zone_power_multiplier = np.array([0.63, 0.82, 0.97, 1.115, 1.35])

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

run_file = 'Run.xlsx'
bike_file = 'Bike.xlsx'
swim_file = 'Swim.xlsx'

run_df = pd.read_excel(run_file, index_col=0, engine='openpyxl')
bike_df = pd.read_excel(bike_file, index_col=0, engine='openpyxl')
swim_df = pd.read_excel(swim_file, engine='openpyxl')

# TODO: swim_df
# TODO: Run when in terms of miles, will need pace
# TODO: Make this one function called three times

for index, row in run_df.iterrows():
    descrip_text = re.split(',|[)]', row['Description'])
    run_df.loc[index, ['Type']] = 'Run'
    run_df.loc[
        index, [zone_1, zone_2, zone_3, zone_4, zone_5, tss, high_duration_head, low_duration_head, intensity_factor,
                normalized_power]] = 0.0
    for period in descrip_text:
        period = period.replace('Minute', 'minute')
        period = period.replace('minute ', 'minutes ')
        period = period.replace(' uphill or simulated', '')
        period = period.replace('uphill', '')
        period = period.replace(' in', '')
        period = period.replace('"', ' seconds')

        if len(period) == 0 or 'mile' in period:
            pass
        elif 'x' in period:  # Detects things like 2 x (20 minutes Zone 2/5 minutes Zone 1)
            split_text = re.split(' x [(]', period)
            multiplier = float(split_text[0])
            zone_split = re.split('[/]', split_text[1])

            if 'minutes' in zone_split[0]:
                high = re.split('minutes', zone_split[0])
                high_duration = float(high[0].strip())
                high_zone = high[1].strip()
            elif 'seconds' in zone_split[0]:
                high = re.split('seconds', zone_split[0])
                high_duration = float(high[0].strip()) / 60.0
                high_zone = high[1].strip()

            if 'rest' in zone_split[1]:
                low_duration = 0
                low_zone = 'Zone 1'
            elif 'minutes' in zone_split[1]:
                low = re.split('minutes', zone_split[1])
                low_duration = float(low[0].strip())
                low_zone = low[1].strip()
            elif 'seconds' in zone_split[1]:
                low = re.split('seconds', zone_split[1])
                low_duration = float(low[0].strip()) / 60.0
                low_zone = low[1].strip()

            run_df.loc[index, [low_zone]] = run_df.loc[index, [low_zone]] + multiplier * low_duration
            run_df.loc[index, [high_zone]] = run_df.loc[index, [high_zone]] + multiplier * high_duration
            run_df.loc[index, [low_duration_head]] = run_df.loc[index, [low_duration_head]] + multiplier * low_duration
            if high_zone == zone_2:
                run_df.loc[index, [low_duration_head]] = run_df.loc[
                                                             index, [low_duration_head]] + multiplier * high_duration
            else:
                run_df.loc[index, [high_duration_head]] = run_df.loc[
                                                          index, [high_duration_head]] + multiplier * high_duration

        else:
            split_text = re.split('minutes', period)
            zone_time = float(split_text[0].strip())
            zone = split_text[1].strip()
            run_df.loc[index, [zone]] = run_df.loc[index, [zone]] + zone_time
            if zone == zone_1 or zone == zone_2:
                run_df.loc[index, [low_duration_head]] = run_df.loc[index, [low_duration_head]] + zone_time
            else:
                run_df.loc[index, [high_duration_head]] = run_df.loc[index, [high_duration_head]] + zone_time

    if len(descrip_text) == 0 or 'mile' in descrip_text:
        run_df.loc[index, [tss]] = 0.0
        pass
    else:
        zone_1_time = float(run_df.loc[index, [zone_1]].tolist()[0])
        zone_2_time = float(run_df.loc[index, [zone_2]].tolist()[0])
        zone_3_time = float(run_df.loc[index, [zone_3]].tolist()[0])
        zone_4_time = float(run_df.loc[index, [zone_4]].tolist()[0])
        zone_5_time = float(run_df.loc[index, [zone_5]].tolist()[0])
        zone_times = np.array([zone_1_time, zone_2_time, zone_3_time, zone_4_time, zone_5_time])
        norm_p, int_f, tss_val = training_stress(zone_times, run_zone_power_multiplier, run_ftp)
        run_df.loc[index, [normalized_power]] = norm_p
        run_df.loc[index, [intensity_factor]] = int_f
        run_df.loc[index, [tss]] = tss_val

run_df.to_excel(run_file, engine='openpyxl')
# raise SystemExit(0)

for index, row in bike_df.iterrows():
    descrip_text = re.split(',|[)]', row['Description'])
    run_df.loc[index, ['Type']] = 'Bike'
    bike_df.loc[index, [zone_1, zone_2, zone_3, zone_4, zone_5, tss, high_duration_head, low_duration_head, tss,
                        intensity_factor, normalized_power]] = 0.0

    for period in descrip_text:
        if len(period) == 0:
            pass
        elif 'x' in period:  # Detects things like 2 x (20 minutes Zone 2/5 minutes Zone 1)
            period = period.replace('minute ', 'minutes ')
            period = period.replace(' uphill or simulated', '')
            split_text = re.split(' x [(]', period)
            multiplier = float(split_text[0])
            zone_split = re.split('[/]', split_text[1])

            if 'minutes' in zone_split[0]:
                high = re.split('minutes', zone_split[0])
                high_duration = float(high[0].strip())
                high_zone = high[1].strip()
            elif 'seconds' in zone_split[0]:
                high = re.split('seconds', zone_split[0])
                high_duration = float(high[0].strip()) / 60.0
                high_zone = high[1].strip()

            if 'minutes' in zone_split[1]:
                low = re.split('minutes', zone_split[1])
                low_duration = float(low[0].strip())
                low_zone = low[1].strip()
            elif 'seconds' in zone_split[1]:
                low = re.split('seconds', zone_split[1])
                low_duration = float(low[0].strip()) / 60.0
                low_zone = low[1].strip()

            bike_df.loc[index, [low_zone]] = bike_df.loc[index, [low_zone]] + multiplier * low_duration
            bike_df.loc[index, [high_zone]] = bike_df.loc[index, [high_zone]] + multiplier * high_duration
            bike_df.loc[index, [low_duration_head]] = bike_df.loc[
                                                          index, [low_duration_head]] + multiplier * low_duration
            if high_zone == zone_2:
                bike_df.loc[index, [low_duration_head]] = bike_df.loc[
                                                             index, [low_duration_head]] + multiplier * high_duration
            else:
                bike_df.loc[index, [high_duration_head]] = bike_df.loc[
                                                          index, [high_duration_head]] + multiplier * high_duration
        else:
            period = period.replace(' in', '')
            split_text = re.split('minutes', period)
            zone_time = float(split_text[0].strip())
            zone = split_text[1].strip()
            bike_df.loc[index, [zone]] = bike_df.loc[index, [zone]] + zone_time
            if zone == zone_1 or zone == zone_2:
                bike_df.loc[index, [low_duration_head]] = bike_df.loc[index, [low_duration_head]] + zone_time
            else:
                bike_df.loc[index, [high_duration_head]] = bike_df.loc[index, [high_duration_head]] + zone_time

    if len(descrip_text) == 0 or 'mile' in descrip_text:
        bike_df.loc[index, [tss]] = 0.0
        pass
    else:
        zone_1_time = float(bike_df.loc[index, [zone_1]].tolist()[0])
        zone_2_time = float(bike_df.loc[index, [zone_2]].tolist()[0])
        zone_3_time = float(bike_df.loc[index, [zone_3]].tolist()[0])
        zone_4_time = float(bike_df.loc[index, [zone_4]].tolist()[0])
        zone_5_time = float(bike_df.loc[index, [zone_5]].tolist()[0])
        zone_times = np.array([zone_1_time, zone_2_time, zone_3_time, zone_4_time, zone_5_time])
        norm_p, int_f, tss_val = training_stress(zone_times, bike_zone_power_multiplier, bike_ftp)
        bike_df.loc[index, [normalized_power]] = norm_p
        bike_df.loc[index, [intensity_factor]] = int_f
        bike_df.loc[index, [tss]] = tss_val
bike_df.to_excel(bike_file, engine='openpyxl')
