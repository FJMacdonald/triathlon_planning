import pandas as pd
import time
import multiprocessing as mp
import random
from classes import triVariables as triv
from util import calculate_plan_score, load_workouts, generate_random_workout_plan
from functools import partial

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# TODO: Allow for bricks
# TODO: Force bricks option
# TODO: Force only easy day /hard days
# TODO: Prefer Intense/Rest cycles

# TODO: Maximize time utilization

# TODO: Not just all Zone 3
# TODO: Prefer Zone 4/5
# TODO: Add Strength
# TODO: exponentially weight distance

# TODO: Be able to force specific workouts (e.g. 5k run)

# TODO: Min/max number of run/bike/swim

# https://www.8020endurance.com/why-endurance-training-cant-be-reduced-to-a-formula/
# – Avoid moving workouts that result in 3 “hard” days in a row. “Hard” means intervals or long workouts.
# – Try to maintain reasonable distribution of each sport. For example, it’s best to cycle every other day than cycle 3 days in a row and not cycle for 4 days.
# – Due to the quick recovery, swim workouts are an exception to the “hard” rule and can be moved at your discretion, while still trying to maintain reasonable swim workout distribution.
# – When performing bike and run workouts back-to-back, it’s best to perform the workout with the most intensity first.
# – Try to keep the workouts all within the same week, as this maintains the precise 80/20 ratios that have been built into your plan.

if __name__ == '__main__':
    wkend_wts_df, wkday_wts_df = load_workouts(triv.run_file, triv.bike_file, triv.swim_file)

    df = generate_random_workout_plan(wkend_wts_df, wkday_wts_df, 10, verbose=True)
    df = df.sort_values(by='Score', ascending=False).reset_index(drop=True)
    print(df)
    # raise SystemExit(0)
    for x in range(30, 31):
        start_time = time.time()
        total_to_run = 100000
        num_cpu = max(mp.cpu_count() - 2, 1)
        num_cpu = x
        num_runs = [int(total_to_run / num_cpu)] * num_cpu
        pool = mp.Pool(num_cpu)
        func = partial(generate_random_workout_plan, wkend_wts_df, wkday_wts_df)
        df = pd.concat(pool.map(func, num_runs))
        pool.close()
        print('Execution Time:', round(time.time() - start_time, 2), 'Num Cores', x)
        df = df.sort_values(by='Score', ascending=False).reset_index(drop=True)
        print(df)
        print(df[df['Score'] >= 90].count().tolist()[0])
        print(100 * round(df[df['Score'] >= 90].count().tolist()[0] / total_to_run, 4))
