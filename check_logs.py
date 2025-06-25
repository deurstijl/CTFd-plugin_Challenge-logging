#!/usr/bin/env python3

import re
import csv
import sys
import os
from datetime import datetime
from collections import defaultdict

# Constants
date_format = "[%m/%d/%Y %H:%M:%S]"

def main(log_folder):
    open_log_file = os.path.join(log_folder, 'challenge_open.log')
    submissions_log_file = os.path.join(log_folder, 'submissions.log')
    output_csv = 'challenge_times.csv'

    # Step 1: Parse open.log
    user_challenge_open_times = defaultdict(dict)  # {user: {challenge_id: open_time}}
    all_usernames = set()

    with open(open_log_file, 'r') as f:
        for line in f:
            match = re.match(r'\[(.*?)\] .*? - (.+?) opened challenge (\d+)', line)
            if match:
                timestamp_str, user, challenge_id = match.groups()
                timestamp = datetime.strptime(f"[{timestamp_str}]", date_format)
                challenge_id = int(challenge_id)

                if challenge_id not in user_challenge_open_times[user]:
                    user_challenge_open_times[user][challenge_id] = timestamp

    # Step 2: Parse submissions.log
    user_challenge_correct_times = defaultdict(dict)  # {user: {challenge_id: correct_time}}

    with open(submissions_log_file, 'r') as f:
        for line in f:
            match = re.match(r'\[(.*?)\] (.+?) submitted .* on (\d+) .* \[CORRECT\]', line)

            if match:
                timestamp_str, user, challenge_id = match.groups()
                timestamp = datetime.strptime(f"[{timestamp_str}]", date_format)
                challenge_id = int(challenge_id)
                all_usernames.add(user)
                if challenge_id not in user_challenge_correct_times[user]:
                    user_challenge_correct_times[user][challenge_id] = timestamp

    # Determine dynamic width for user column
    max_user_len = max((len(user) for user in all_usernames), default=10)
    user_col_width = max(20, max_user_len + 2)

    # Step 3: Write to CSV and print to stdout
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['user', 'challenge_id', 'open_time', 'correct_time', 'time_delta_seconds', 'solved_within_1_min']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Print header
        print(f"{'User':<{user_col_width}}{'Challenge':<11}{'Open Time':<22}{'Correct Time':<22}{'Time Delta':<18}{'<1 min'}")
        print("-" * 99)

        for user in user_challenge_open_times:
            for challenge_id, open_time in user_challenge_open_times[user].items():
                correct_time = user_challenge_correct_times[user].get(challenge_id)
                if correct_time:
                    delta = correct_time - open_time
                    delta_seconds = int(delta.total_seconds())
                    solved_quickly = 'yes' if delta_seconds <= 60 else 'no'

                    writer.writerow({
                        'user': user,
                        'challenge_id': challenge_id,
                        'open_time': open_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'correct_time': correct_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'time_delta_seconds': delta_seconds,
                        'solved_within_1_min': solved_quickly
                    })
                    print(f"{user:<{user_col_width}}{challenge_id:<11}{open_time.strftime('%Y-%m-%d %H:%M:%S'):<22}{correct_time.strftime('%Y-%m-%d %H:%M:%S'):<22}{str(delta):<18}{solved_quickly}")


    print(f"\nResults written to {output_csv}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <CTFd_log_folder>")
        sys.exit(1)
    
    log_folder = sys.argv[1]
    main(log_folder)
