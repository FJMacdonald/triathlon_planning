import pandas as pd
import time
import multiprocessing as mp
import random
from classes import triVariables as triv
from util import calculate_plan_score, load_workouts, generate_random_workout

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# TODO: Allow for bricks
# TODO: Force bricks option
# TODO: Not just all Zone 3
# TODO: Prefer Intense/Rest cycles
# TODO: Add Swim Workouts
# TODO: Add Strength
# TODO: exponentially weight distance

if __name__ == '__main__':
    wkend_wts_df, wkday_wts_df = load_workouts(triv.run_file, triv.bike_file, triv.swim_file)

    print(generate_random_workout(wkend_wts_df, wkday_wts_df, 100, verbose=True))
    raise SystemExit(0)
    start_time = time.time()
    total_to_run = 10000
    num_cpu = max(mp.cpu_count() - 2, 1)
    num_runs = [int(total_to_run / num_cpu)] * num_cpu
    pool = mp.Pool(num_cpu)
    df = pd.concat(pool.map(generate_random_workout, num_runs))
    pool.close()
    print('Run Time:', round(time.time() - start_time, 2))
    df = df.sort_values(by='Score', ascending=False).reset_index(drop=True)
    print(df)
    print(df[df['Score'] >= 90].count().tolist()[0])
    print(100 * round(df[df['Score'] >= 90].count().tolist()[0] / total_to_run, 4))
