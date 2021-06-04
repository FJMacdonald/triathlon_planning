import pandas as pd
import time
import multiprocessing as mp
import random
from classes import triVariables as triv

def load_workouts(run_file, bike_file, swim_file):
    run_df = pd.read_excel(run_file, index_col=0, engine='openpyxl')
    bike_df = pd.read_excel(bike_file, index_col=0, engine='openpyxl')
    # swim_df = pd.read_excel(swim_file, index_col=0, engine='openpyxl')

    run_df = run_df[run_df['TSS'] != 0]
    run_df = run_df[run_df['TSS'].notnull()]

    bike_df = bike_df[bike_df['TSS'] != 0]
    bike_df = bike_df[bike_df['TSS'].notnull()]

    run_wkday_df = run_df[run_df['Duration/Distance'] <= triv.max_time_weekend]
    bike_wkday_df = bike_df[bike_df['Duration/Distance'] <= triv.max_time_weekend]

    run_wkday_df = run_wkday_df[run_wkday_df['TSS'] <= triv.max_time_weekend]
    bike_wkday_df = bike_wkday_df[bike_wkday_df['TSS'] <= triv.max_tss_weekend]

    wkend_wts_df = pd.concat([run_wkday_df, bike_wkday_df], ignore_index=True)

    run_wkend_df = run_df[run_df['Duration/Distance'] <= triv.max_time_weekday]
    bike_wkend_df = bike_df[bike_df['Duration/Distance'] <= triv.max_time_weekday]

    run_wkend_df = run_wkend_df[run_wkend_df['TSS'] <= triv.max_time_weekday]
    bike_wkend_df = bike_wkend_df[bike_wkend_df['TSS'] <= triv.max_tss_weekday]

    wkday_wts_df = pd.concat([run_wkend_df, bike_wkend_df], ignore_index=True)

    return wkend_wts_df, wkday_wts_df

def calculate_plan_score(wkt_plan_tss=0.0,
                         wkt_plan_duration=0.0,
                         wkt_plan_bike_dur=0.0,
                         wkt_plan_run_dur=0.0,
                         wkt_plan_bike_tss=0.0,
                         wkt_plan_run_tss=0.0,
                         wkt_bike_high_dur=0.0,
                         wkt_bike_low_dur=0.0,
                         wkt_run_high_dur=0.0,
                         wkt_run_low_dur=0.0,
                         wkt_high_dur=0.0,
                         wkt_low_dur=0.0,
                         verbose=False
                         ):
    tot_weights = 5.0
    tot_tss_weight = 1.0 / tot_weights  # Overall TSS score weight
    tgt_weight = 1.0 / tot_weights  # Overall 80/20 score weight
    # rbs = run, bike, swim
    rbs_dur_split_weight = 1.0 / tot_weights  # RBS Duration 2/3-1/3 score weight
    rbs_tss_split_weight = 1.0 / tot_weights  # RBS TSS 1/3-1/3 score weight
    rbs_dur_tgt_split_weight = 1.0 / tot_weights  # RBS Duration is 80/20 score weight (i.e. 80% of
    dist_metric_exponential = 1  # Basically how much to punish values which are far away from the target, better to have everything off by 0.1 than everything spot on and one off by 0.08

    tss_score = 1.0 - abs(1.0 - wkt_plan_tss / triv.target_tss)
    if verbose: print('TSS Score:', round(tss_score, 2), 'TSS:', wkt_plan_tss)
    tss_score *= tot_tss_weight

    # ----------------------------------------------
    high_dur_percent = wkt_high_dur / wkt_plan_duration
    low_dur_percent = wkt_low_dur / wkt_plan_duration

    high_tgt_score = 1.0 - abs(1.0 - high_dur_percent / triv.high_tgt)
    low_tgt_score = 1.0 - abs(1.0 - low_dur_percent / triv.low_tgt)
    if verbose: print('High TGT Score:', round(high_tgt_score, 2), 'High %:', round(high_dur_percent, 2))
    if verbose: print('Low TGT Score:', round(low_tgt_score, 2), 'Low %:', round(low_dur_percent, 2))

    high_tgt_score *= (tgt_weight / 2)
    low_tgt_score *= (tgt_weight / 2)
    tgt_score = high_tgt_score + low_tgt_score

    # ----------------------------------------------
    run_dur_percent = wkt_plan_run_dur / wkt_plan_duration
    bike_dur_percent = wkt_plan_bike_dur / wkt_plan_duration

    run_dur_tgt_score = 1.0 - abs(1.0 - run_dur_percent / triv.run_tgt_percent)
    bike_dur_tgt_score = 1.0 - abs(1.0 - bike_dur_percent / triv.bike_tgt_percent)
    if verbose: print('Run Dur % TGT Score:', round(run_dur_tgt_score, 2), 'Run Dur %:', round(run_dur_percent, 2),
                      'Total Run Dur:', wkt_plan_run_dur)
    if verbose: print('Bike Dur % TGT Score:', round(bike_dur_tgt_score, 2), 'Bike Dur %:', round(bike_dur_percent, 2),
                      'Total Bike Dur:', wkt_plan_bike_dur)
    run_dur_tgt_score *= rbs_dur_split_weight / 2
    bike_dur_tgt_score *= rbs_dur_split_weight / 2

    dur_tgt_score = run_dur_tgt_score + bike_dur_tgt_score

    # ----------------------------------------------
    run_tss_percent = wkt_plan_run_tss / wkt_plan_tss
    bike_tss_percent = wkt_plan_bike_tss / wkt_plan_tss

    run_tss_tgt_score = 1.0 - abs(1.0 - run_tss_percent / triv.run_tgt_percent)
    bike_tss_tgt_score = 1.0 - abs(1.0 - bike_tss_percent / triv.bike_tgt_percent)
    if verbose: print('Run TSS % TGT Score:', round(run_tss_tgt_score, 2), 'Run TSS %:', round(run_tss_percent, 2),
                      'Total Run TSS:', wkt_plan_run_tss)
    if verbose: print('Bike TSS % TGT Score:', round(bike_tss_tgt_score, 2), 'Bike TSS %:', round(bike_tss_percent, 2),
                      'Total Bike TSS:', wkt_plan_bike_tss)
    run_tss_tgt_score *= rbs_tss_split_weight / 2
    bike_tss_tgt_score *= rbs_tss_split_weight / 2

    tss_tgt_score = run_tss_tgt_score + bike_tss_tgt_score

    # ----------------------------------------------
    run_high_dur_percent = wkt_run_high_dur / wkt_plan_run_dur
    run_low_dur_percent = wkt_run_low_dur / wkt_plan_run_dur

    bike_high_dur_percent = wkt_bike_high_dur / wkt_plan_bike_dur
    bike_low_dur_percent = wkt_bike_low_dur / wkt_plan_bike_dur

    run_high_tgt_score = 1.0 - abs(1.0 - run_high_dur_percent / triv.high_tgt)
    run_low_tgt_score = 1.0 - abs(1.0 - run_low_dur_percent / triv.low_tgt)

    bike_high_tgt_score = 1.0 - abs(1.0 - bike_high_dur_percent / triv.high_tgt)
    bike_low_tgt_score = 1.0 - abs(1.0 - bike_low_dur_percent / triv.low_tgt)

    if verbose: print('Run High TGT Score:', round(run_high_tgt_score, 2), 'Run High %:',
                      round(run_high_dur_percent, 2))
    if verbose: print('Run Low TGT Score:', round(run_low_tgt_score, 2), 'Run Low %:', round(run_low_dur_percent, 2))
    if verbose: print('Bike High TGT Score:', round(bike_high_tgt_score, 2), 'Bike High %:',
                      round(bike_high_dur_percent, 2))
    if verbose: print('Bike Low TGT Score:', round(bike_low_tgt_score, 2), 'Bike Low %:',
                      round(bike_low_dur_percent, 2))

    run_dur_spt_score = (run_high_tgt_score + run_low_tgt_score) / 2
    bike_dur_spt_score = (bike_high_tgt_score + bike_low_tgt_score) / 2

    dur_split_tgt_score = rbs_dur_tgt_split_weight * (run_dur_spt_score + bike_dur_spt_score) / 2

    return round(tss_score + tgt_score + dur_tgt_score + tss_tgt_score + dur_split_tgt_score,
                 4) * 100, high_dur_percent, low_dur_percent, run_dur_percent, bike_dur_percent, run_tss_percent, bike_tss_percent, run_high_dur_percent, run_low_dur_percent, bike_high_dur_percent, bike_low_dur_percent



# 10000 take 30 seconds
def generate_random_workout(wkend_wts_df, wkday_wts_df, num_gen, verbose=False):
    wkt_dict = {'Workouts'       : [],
                'Score'          : [],
                'Total Duration' : [],
                'Total TSS'      : [],
                '% Bike Dur'     : [],
                '% Run Dur'      : [],
                '% High Dur'     : [],
                '% Low Dur'      : [],
                '% Run TSS'      : [],
                '% Bike TSS'     : [],
                '% High Run Dur' : [],
                '% Low Run Dur'  : [],
                '% High Bike Dur': [],
                '% Low Bike Dur' : [], }
    wkts_df = pd.DataFrame(wkt_dict)

    for i in range(num_gen):
        # We will always want at least one run and one bike on weekdays
        run_wkday = wkday_wts_df[wkday_wts_df['Type'] == 'Run'].sample()
        bike_wkday = wkday_wts_df[wkday_wts_df['Type'] == 'Bike'].sample()

        # Get a random workout for every weekday, shuffle them up and assign
        wkday_wkts = wkday_wts_df.sample(len(triv.weekdays) - 2)
        wkday_wkts = pd.concat([run_wkday, bike_wkday, wkday_wkts], ignore_index=True)
        wkday_wkts = wkday_wkts.sample(frac=1)
        wkday_wkts['Weekday'] = triv.weekdays
        wkday_wkts['TSS/Min'] = wkday_wkts[triv.tss].div(triv.max_time_weekday)

        wkend_wkts = wkend_wts_df.sample(len(triv.weekend))
        wkend_wkts['Weekday'] = triv.weekend
        wkend_wkts['TSS/Min'] = wkend_wkts[triv.tss].div(triv.max_time_weekend)

        wkts = pd.concat([wkday_wkts, wkend_wkts], ignore_index=True)
        del wkts['Description']

        wkt_plan_tss = wkts[triv.tss].sum()
        wkt_plan_duration = wkts[triv.duration].sum()
        wkt_high_dur = wkts[triv.high_duration].sum()
        wkt_high_pct = wkt_high_dur / wkt_plan_duration

        bike_wkts = wkts.loc[wkts['Type'] == 'Bike']
        wkt_plan_bike_dur = bike_wkts[triv.duration].sum()
        bike_dur_percent = wkt_plan_bike_dur / wkt_plan_duration
        cnt = 0

        # TODO: Check Bike Condition
        # TODO: Allow for Bricks
        while wkt_plan_tss < triv.target_tss * 0.95 \
                or wkt_plan_tss > triv.target_tss * 1.05 \
                or wkt_high_pct < triv.high_tgt * 0.75 \
                or wkt_high_pct > triv.high_tgt * 1.25:
            # or bike_dur_percent < bike_tgt * 0.75 \
            # or bike_dur_percent > bike_tgt * 1.25:
            replace_day = ''
            if wkt_plan_tss < triv.target_tss * 0.95 or wkt_high_pct < triv.high_tgt * 0.75:
                replace_day = wkts[['TSS/Min']].idxmin().tolist()[0]
            elif wkt_plan_tss > triv.target_tss * 1.05 or wkt_high_pct > triv.high_tgt * 1.25:
                replace_day = wkts[['TSS/Min']].idxmax().tolist()[0]
            # elif bike_dur_percent < bike_tgt * 0.75:
            # Could replace the smallest bike workout with a longer one
            # Could replace a run workout with a bike workout
            # Could replace longest run with a shorter run

            if wkts.loc[[replace_day]].Weekday.isin(['Sat', 'Sun']).any():
                replace_workout = wkend_wts_df.sample(1)
                replace_workout['Weekday'] = wkts.loc[[replace_day]].Weekday.tolist()[0]
                replace_workout['TSS/Min'] = replace_workout[triv.tss].div(triv.max_time_weekend)
            else:
                replace_workout = wkday_wts_df.sample(1)
                replace_workout['Weekday'] = wkts.loc[[replace_day]].Weekday.tolist()[0]
                replace_workout['TSS/Min'] = replace_workout[triv.tss].div(triv.max_time_weekday)

            wkts = wkts.drop(replace_day)
            wkts = wkts.append(replace_workout, ignore_index=True)

            wkt_plan_tss = wkts[triv.tss].sum()
            wkt_plan_duration = wkts[triv.duration].sum()
            wkt_high_dur = wkts[triv.high_duration].sum()
            wkt_high_pct = wkt_high_dur / wkt_plan_duration

            bike_wkts = wkts.loc[wkts['Type'] == 'Bike']
            wkt_plan_bike_dur = bike_wkts[triv.duration].sum()
            bike_dur_percent = wkt_plan_bike_dur / wkt_plan_duration
            cnt += 1
            if cnt > 25:  # If after 25 changes it doesn't work, just break
                break

        # TODO: Make weekday, weekend columns
        # TODO: Sort output high day, low day, trying to alternate bike/run
        # Assign each workout to day of the week - DONE
        # Check if sum within TSS bound (0.95, 1.05) - DONE
        # If less than TSS, find day with lowest TSS/(total_allowed_time)
        #   if ratio < 0.4, just replace it with a new workout
        #   if greater, randomly replace it or add a new workout (80% replace, 20% add new)
        #   make sure sum of each days workouts does not exceed limit, if it does just wipe out the whole day and try again
        # if greater than TSS, find day with highest TSS/hour
        #

        wkt_plan_tss = wkts[triv.tss].sum()
        wkt_plan_duration = wkts[triv.duration].sum()
        wkt_high_dur = wkts[triv.high_duration].sum()
        wkt_high_pct = wkt_high_dur / wkt_plan_duration

        bike_wkts = wkts.loc[wkts[triv.type] == 'Bike']
        wkt_plan_bike_dur = bike_wkts[triv.duration].sum()
        bike_dur_percent = wkt_plan_bike_dur / wkt_plan_duration
        # print(wkts)

        if triv.target_tss * 0.95 < wkt_plan_tss < triv.target_tss * 1.05 \
                and triv.high_tgt * 0.75 < wkt_high_pct < triv.high_tgt * 1.25 \
                and triv.bike_tgt * 0.75 < bike_dur_percent < triv.bike_tgt * 1.25:
            wkt_plan = wkts[triv.code].to_list()

            # Sum Run stats
            run_wkts = wkts.loc[wkts[triv.type] == 'Run']
            wkt_plan_run_dur = run_wkts[triv.duration].sum()
            wkt_run_high_dur = run_wkts[triv.high_duration].sum()
            wkt_run_low_dur = run_wkts[triv.low_duration].sum()
            wkt_plan_run_tss = run_wkts[triv.tss].sum()

            # Sum Bike stats
            wkt_bike_high_dur = bike_wkts[triv.high_duration].sum()
            wkt_bike_low_dur = bike_wkts[triv.low_duration].sum()
            wkt_plan_bike_tss = bike_wkts[triv.tss].sum()
            wkt_low_dur = wkt_run_low_dur + wkt_bike_low_dur

            wkt_score, high_dur_percent, low_dur_percent, run_dur_percent, bike_dur_percent, run_tss_percent, bike_tss_percent, run_high_dur_percent, run_low_dur_percent, bike_high_dur_percent, bike_low_dur_percent = calculate_plan_score(
                    wkt_plan_tss,
                    wkt_plan_duration,
                    wkt_plan_bike_dur,
                    wkt_plan_run_dur,
                    wkt_plan_bike_tss,
                    wkt_plan_run_tss,
                    wkt_bike_high_dur,
                    wkt_bike_low_dur,
                    wkt_run_high_dur,
                    wkt_run_low_dur,
                    wkt_high_dur,
                    wkt_low_dur,
                    verbose=verbose
            )
            wkt_dict = {'Workouts'       : wkt_plan,
                        'Score'          : wkt_score,
                        'Total Duration' : wkt_plan_duration,
                        'Total TSS'      : wkt_plan_tss,
                        '% Bike Dur'     : round(bike_dur_percent, 2),
                        '% Run Dur'      : round(run_dur_percent, 2),
                        '% High Dur'     : round(high_dur_percent, 2),
                        '% Low Dur'      : round(low_dur_percent, 2),
                        '% Run TSS'      : round(run_tss_percent, 2),
                        '% Bike TSS'     : round(bike_tss_percent, 2),
                        '% High Run Dur' : round(run_high_dur_percent, 2),
                        '% Low Run Dur'  : round(run_low_dur_percent, 2),
                        '% High Bike Dur': round(bike_high_dur_percent, 2),
                        '% Low Bike Dur' : round(bike_low_dur_percent, 2)}
            wkts_df = wkts_df.append(wkt_dict, ignore_index=True)
    return wkts_df
