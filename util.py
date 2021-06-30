import pandas as pd
import time
import multiprocessing as mp
import random
from classes import triVariables as triv, workout


def load_workouts(run_file, bike_file, swim_file):
    df = pd.DataFrame()

    if triv.run_tgt_percent > 0:
        run_df = pd.read_excel(run_file, index_col=0, engine='openpyxl')
        df = pd.concat([df, run_df], ignore_index=True)
    if triv.bike_tgt_percent > 0:
        bike_df = pd.read_excel(bike_file, index_col=0, engine='openpyxl')
        df = pd.concat([df, bike_df], ignore_index=True)
    if triv.swim_tgt_percent > 0:
        swim_df = pd.read_excel(swim_file, index_col=0, engine='openpyxl')
        df = pd.concat([df, swim_df], ignore_index=True)

    df = df[df['TSS'] != 0]
    df = df[df['TSS'].notnull()]

    wkend_wts_df = df[df['Duration'] <= triv.max_time_weekend]
    wkend_wts_df = wkend_wts_df[wkend_wts_df['TSS'] <= triv.max_time_weekend]

    wkday_wts_df = df[df['Duration'] <= triv.max_time_weekday]
    wkday_wts_df = wkday_wts_df[wkday_wts_df['TSS'] <= triv.max_time_weekday]

    return wkend_wts_df, wkday_wts_df


def calculate_plan_score(wkt, verbose=False):
    def calculate_sport_scores(wkt, exer):
        exer.dur_percent = exer.dur / wkt.duration
        spt_dur_tgt_score = 1.0 - abs(1.0 - exer.dur_percent / exer.tgt_percent)
        if verbose: print(exer.name, 'Dur % TGT Score:', round(spt_dur_tgt_score, 2), exer.name, 'Dur %:',
                          round(exer.dur_percent, 2), 'Total', exer.name, 'Dur:', exer.dur)

        spt_dur_tgt_score *= triv.rbs_dur_split_weight * exer.tgt_percent

        exer.tss_percent = exer.tss / wkt.total_tss
        spt_tss_tgt_score = 1.0 - abs(1.0 - exer.tss_percent / exer.tgt_percent)
        if verbose: print(exer.name, 'TSS % TGT Score:', round(spt_tss_tgt_score, 2), exer.name, 'TSS %:',
                          round(exer.tss_percent, 2), 'Total', exer.name, 'TSS:', exer.tss)
        spt_tss_tgt_score *= triv.rbs_tss_split_weight * exer.tgt_percent

        exer.high_dur_percent = ((0.0 or exer.high_dur) / exer.dur or 0.0)
        exer.low_dur_percent = exer.low_dur / exer.dur

        spt_high_tgt_score = 1.0 - abs(1.0 - exer.high_dur_percent / triv.high_tgt)
        spt_low_tgt_score = 1.0 - abs(1.0 - exer.low_dur_percent / triv.low_tgt)

        if verbose: print(exer.name, 'High TGT Score:', round(spt_high_tgt_score, 2), exer.name, 'High %:',
                          round(exer.high_dur_percent, 2))
        if verbose: print(exer.name, 'Low TGT Score:', round(spt_low_tgt_score, 2), exer.name, 'Low %:',
                          +    round(exer.low_dur_percent, 2))
        dur_split_tgt_score = (
                                      spt_high_tgt_score + spt_low_tgt_score) / 2 * exer.tgt_percent * triv.rbs_dur_tgt_split_weight

        exer.zone_3_percent = exer.zone_3 / exer.high_dur
        if pd.isna(exer.zone_3_percent): exer.zone_3_percent = 0.0
        spt_z3_tgt_score = 1.0 - abs(1.0 - exer.zone_3_percent / triv.zone_3_tgt)
        exer.zone_4_percent = exer.zone_4 / exer.high_dur
        if pd.isna(exer.zone_4_percent): exer.zone_4_percent = 0.0
        spt_z4_tgt_score = 1.0 - abs(1.0 - exer.zone_4_percent / triv.zone_4_tgt)
        exer.zone_5_percent = exer.zone_5 / exer.high_dur
        if pd.isna(exer.zone_5_percent): exer.zone_5_percent = 0.0
        spt_z5_tgt_score = 1.0 - abs(1.0 - exer.zone_5_percent / triv.zone_5_tgt)

        if verbose: print(exer.name, 'Zone 3 TGT Score:', round(spt_z3_tgt_score, 2), exer.name, 'Zone 3 %:',
                          round(exer.zone_3_percent, 2))
        if verbose: print(exer.name, 'Zone 4 TGT Score:', round(spt_z4_tgt_score, 2), exer.name, 'Zone 4 %:',
                          +    round(exer.zone_4_percent, 2))
        if verbose: print(exer.name, 'Zone 5 TGT Score:', round(spt_z5_tgt_score, 2), exer.name, 'Zone 5 %:',
                          +    round(exer.zone_5_percent, 2))
        high_split_tgt_score = (
                                       spt_z3_tgt_score + spt_z4_tgt_score + spt_z5_tgt_score) / 3 * exer.tgt_percent * triv.high_zone_split_weight

        wkt.tss_tgt_score += spt_tss_tgt_score
        wkt.dur_tgt_score += spt_dur_tgt_score
        wkt.dur_split_tgt_score += dur_split_tgt_score
        wkt.high_split_tgt_score += high_split_tgt_score

    if triv.tot_tss_weight > 0.0:
        wkt.tss_score = 1.0 - abs(1.0 - wkt.total_tss / triv.target_tss)
        if verbose: print('TSS Score:', round(wkt.tss_score, 2), 'TSS:', wkt.total_tss)
        wkt.tss_score *= triv.tot_tss_weight

    # ----------------------------------------------
    if triv.tgt_weight > 0.0:
        wkt.high_dur_percent = wkt.high_dur / wkt.duration
        wkt.low_dur_percent = wkt.low_dur / wkt.duration

        wkt.high_tgt_score = 1.0 - abs(1.0 - wkt.high_dur_percent / triv.high_tgt)
        wkt.low_tgt_score = 1.0 - abs(1.0 - wkt.low_dur_percent / triv.low_tgt)
        if verbose: print('High TGT Score:', round(wkt.high_tgt_score, 2), 'High %:', round(wkt.high_dur_percent, 2))
        if verbose: print('Low TGT Score:', round(wkt.low_tgt_score, 2), 'Low %:', round(wkt.low_dur_percent, 2))

        wkt.tgt_score = (wkt.high_tgt_score + wkt.low_tgt_score) * triv.tgt_weight / 2

    # ----------------------------------------------
    if triv.run_tgt_percent > 0.0:
        calculate_sport_scores(wkt, wkt.run)

    if triv.bike_tgt_percent > 0.0:
        calculate_sport_scores(wkt, wkt.bike)

    if triv.swim_tgt_percent > 0.0:
        calculate_sport_scores(wkt, wkt.swim)

    # ----------------------------------------------
    wkt.score = round(
            wkt.tss_score + wkt.tgt_score + wkt.dur_tgt_score + wkt.tss_tgt_score + wkt.dur_split_tgt_score + wkt.high_split_tgt_score,
            4) * 100


# 10000 take 30 seconds
def generate_random_workout_plan(wkend_wts_df, wkday_wts_df, num_gen, verbose=False):
    wkt_dict = {'Workouts'        : [],
                'Score'           : [],
                'Total Duration'  : [],
                'Total TSS'       : [],
                '% Run Dur'       : [],
                '% Bike Dur'      : [],
                '% Swim Dur'      : [],
                '% High Dur'      : [],
                '% Low Dur'       : [],
                '% Run TSS'       : [],
                '% Bike TSS'      : [],
                '% Swim TSS'      : [],
                '% High Run Dur'  : [],
                '% Low Run Dur'   : [],
                'Z3/4/5 Run Dist' : [],
                '% High Bike Dur' : [],
                '% Low Bike Dur'  : [],
                'Z3/4/5 Bike Dist': [],
                '% High Swim Dur' : [],
                '% Low Swim Dur'  : [],
                'Z3/4/5 Swim Dist': [], }
    wkts_df = pd.DataFrame(wkt_dict)

    for i in range(num_gen):
        if verbose: print('-----------------------------------')
        wkt = workout()
        # We will always want at least one run and one bike on weekdays
        wkts = pd.DataFrame()
        tot_wkts = 0
        if triv.run_tgt_percent > 0:
            wkts = wkts.append(wkday_wts_df[wkday_wts_df['Type'] == 'Run'].sample())
            tot_wkts += 1
            wkt.run.tgt_percent = triv.run_tgt_percent
        if triv.bike_tgt_percent > 0:
            wkts = wkts.append(wkday_wts_df[wkday_wts_df['Type'] == 'Bike'].sample())
            tot_wkts += 1
            wkt.bike.tgt_percent = triv.bike_tgt_percent
        if triv.swim_tgt_percent > 0:
            wkts = wkts.append(wkday_wts_df[wkday_wts_df['Type'] == 'Swim'].sample())
            tot_wkts += 1
            wkt.swim.tgt_percent = triv.swim_tgt_percent

        # Get a random workout for every weekday, shuffle them up and assign
        wkday_wkts = wkday_wts_df.sample(len(triv.weekdays) - tot_wkts)
        wkday_wkts = pd.concat([wkts, wkday_wkts], ignore_index=True)
        wkday_wkts = wkday_wkts.sample(frac=1)
        wkday_wkts['Weekday'] = triv.weekdays
        wkday_wkts['TSS/Min'] = wkday_wkts[triv.tss].div(triv.max_time_weekday)

        wkend_wkts = wkend_wts_df.sample(len(triv.weekend))
        wkend_wkts['Weekday'] = triv.weekend
        wkend_wkts['TSS/Min'] = wkend_wkts[triv.tss].div(triv.max_time_weekend)

        wkts = pd.concat([wkday_wkts, wkend_wkts], ignore_index=True)
        del wkts['Description']

        wkt.total_tss = wkts[triv.tss].sum()
        wkt.duration = wkts[triv.duration].sum()
        wkt.high_dur = wkts[triv.high_duration_head].sum()
        wkt.high_pct = wkt.high_dur / wkt.duration

        cnt = 0

        # TODO: Check Bike Condition
        # TODO: Allow for Bricks
        while wkt.total_tss < triv.target_tss * 0.95 \
                or wkt.total_tss > triv.target_tss * 1.05 \
                or wkt.high_pct < triv.high_tgt * 0.75 \
                or wkt.high_pct > triv.high_tgt * 1.25:
            replace_day = ''
            if wkt.total_tss < triv.target_tss * 0.95 or wkt.high_pct < triv.high_tgt * 0.75:
                replace_day = wkts[['TSS/Min']].idxmin().tolist()[0]
            elif wkt.total_tss > triv.target_tss * 1.05 or wkt.high_pct > triv.high_tgt * 1.25:
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

            wkt.total_tss = wkts[triv.tss].sum()
            wkt.duration = wkts[triv.duration].sum()
            wkt.high_dur = wkts[triv.high_duration_head].sum()
            wkt.high_pct = wkt.high_dur / wkt.duration

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

        wkt.total_tss = wkts[triv.tss].sum()
        wkt.duration = wkts[triv.duration].sum()
        wkt.high_dur = wkts[triv.high_duration_head].sum()
        wkt.high_pct = wkt.high_dur / wkt.duration

        # print(wkts)

        if triv.target_tss * 0.95 < wkt.total_tss < triv.target_tss * 1.05 \
                and triv.high_tgt * 0.75 < wkt.high_pct < triv.high_tgt * 1.25 and wkt.high_dur > 0.0:
            # and triv.bike_tgt_percent * 0.75 < bike_dur_percent < triv.bike_tgt_percent * 1.25:

            wkt.plan = wkts[triv.code].to_list()
            wkt.low_dur = 0.0

            # Sum Run stats
            if triv.run_tgt_percent > 0.0:
                run_wkts = wkts.loc[wkts[triv.type] == 'Run']
                wkt.run.dur = run_wkts[triv.duration].sum()
                wkt.run.high_dur = run_wkts[triv.high_duration_head].sum()
                wkt.run.zone_3 = run_wkts[triv.zone_3].sum()
                wkt.run.zone_4 = run_wkts[triv.zone_4].sum()
                wkt.run.zone_5 = run_wkts[triv.zone_5].sum()
                wkt.run.low_dur = run_wkts[triv.low_duration_head].sum()
                wkt.run.tss = run_wkts[triv.tss].sum()
                wkt.low_dur += wkt.run.low_dur

            # Sum Bike stats
            if triv.bike_tgt_percent > 0.0:
                bike_wkts = wkts.loc[wkts[triv.type] == 'Bike']
                wkt.bike.dur = bike_wkts[triv.duration].sum()
                wkt.bike.high_dur = bike_wkts[triv.high_duration_head].sum()
                wkt.bike.low_dur = bike_wkts[triv.low_duration_head].sum()
                wkt.bike.zone_3 = bike_wkts[triv.zone_3].sum()
                wkt.bike.zone_4 = bike_wkts[triv.zone_4].sum()
                wkt.bike.zone_5 = bike_wkts[triv.zone_5].sum()
                wkt.bike.tss = bike_wkts[triv.tss].sum()
                wkt.low_dur += wkt.bike.low_dur

            # Sum Swim stats
            if triv.swim_tgt_percent > 0.0:
                swim_wkts = wkts.loc[wkts[triv.type] == 'Swim']
                wkt.swim.dur = swim_wkts[triv.duration].sum()
                wkt.swim.high_dur = swim_wkts[triv.high_duration_head].sum()
                wkt.swim.low_dur = swim_wkts[triv.low_duration_head].sum()
                wkt.swim.zone_3 = swim_wkts[triv.zone_3].sum()
                wkt.swim.zone_4 = swim_wkts[triv.zone_4].sum()
                wkt.swim.zone_5 = swim_wkts[triv.zone_5].sum()
                wkt.swim.tss = swim_wkts[triv.tss].sum()
                wkt.low_dur += wkt.swim.low_dur

            calculate_plan_score(wkt, verbose=verbose)

            wkt_dict = {'Workouts'        : wkt.plan,
                        'Score'           : wkt.score,
                        'Total Duration'  : wkt.duration,
                        'Total TSS'       : wkt.total_tss,
                        '% Bike Dur'      : round(wkt.bike.dur_percent, 2),
                        '% Run Dur'       : round(wkt.run.dur_percent, 2),
                        '% Swim Dur'      : round(wkt.swim.dur_percent, 2),
                        '% High Dur'      : round(wkt.high_dur_percent, 2),
                        '% Low Dur'       : round(wkt.low_dur_percent, 2),
                        '% Run TSS'       : round(wkt.run.tss_percent, 2),
                        '% Bike TSS'      : round(wkt.bike.tss_percent, 2),
                        '% Swim TSS'      : round(wkt.swim.tss_percent, 2),
                        '% High Run Dur'  : round(wkt.run.high_dur_percent, 2),
                        '% Low Run Dur'   : round(wkt.run.low_dur_percent, 2),
                        'Z3/4/5 Run Dist' : f"{int(100 * wkt.run.zone_3_percent)}/{int(100 * wkt.run.zone_4_percent)}/{int(100 * wkt.run.zone_5_percent)}",
                        '% High Bike Dur' : round(wkt.bike.high_dur_percent, 2),
                        '% Low Bike Dur'  : round(wkt.bike.low_dur_percent, 2),
                        'Z3/4/5 Bike Dist': f"{int(100 * wkt.bike.zone_3_percent)}/{int(100 * wkt.bike.zone_4_percent)}/{int(100 * wkt.bike.zone_5_percent)}",
                        '% High Swim Dur' : round(wkt.swim.high_dur_percent, 2),
                        '% Low Swim Dur'  : round(wkt.swim.low_dur_percent, 2),
                        'Z3/4/5 Swim Dist': f"{int(100 * wkt.swim.zone_3_percent)}/{int(100 * wkt.swim.zone_4_percent)}/{int(100 * wkt.swim.zone_5_percent)}",
                        }
            wkts_df = wkts_df.append(wkt_dict, ignore_index=True)

    if triv.run_tgt_percent == 0.0:
        wkts_df = wkts_df.drop(columns=['% Run Dur', '% Run TSS', '% High Run Dur', '% Low Run Dur', 'Z3/4/5 Run Dist'])

    if triv.bike_tgt_percent == 0.0:
        wkts_df = wkts_df.drop(
            columns=['% Bike Dur', '% Bike TSS', '% High Bike Dur', '% Low Bike Dur', 'Z3/4/5 Bike Dist'])

    if triv.swim_tgt_percent == 0.0:
        wkts_df = wkts_df.drop(
            columns=['% Swim Dur', '% Swim TSS', '% High Swim Dur', '% Low Swim Dur', 'Z3/4/5 Swim Dist'])

    return wkts_df
