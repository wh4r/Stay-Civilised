import os
import sys

import numpy as np

# The whole app reads/writes data relative to the current working directory
# (demand files, saves, log). Match that here so frozen and dev builds agree.
BASE_DIR = os.getcwd()

DAILY_AMPLITUDE = 100          # Daily demand variation
SEASONAL_AMPLITUDE = 60        # Seasonal demand variation
NOISE_AMPLITUDE = 30           # Random noise
BASE_DEMAND = 1000             # Average demand

MINUTES_PER_DAY = 24 * 60


def demand_path(day):
    """Path to the saved demand file for a given day (1-indexed)."""
    return os.path.join(BASE_DIR, "demand", f"day_{day:03d}.txt")


def generate_demand(seed, days=364):
    """Generates the full demand profile for a given seed and writes it to files.

    Returns the number of day files created.
    """
    np.random.seed(seed)

    total_minutes = days * MINUTES_PER_DAY
    t = np.arange(total_minutes)
    time_days = t / MINUTES_PER_DAY

    daily = DAILY_AMPLITUDE * np.cos(2 * np.pi * time_days - np.pi)
    seasonal = SEASONAL_AMPLITUDE * np.sin(2 * np.pi * time_days / days)
    noise = np.random.uniform(-NOISE_AMPLITUDE, NOISE_AMPLITUDE, total_minutes)

    demand = BASE_DEMAND + daily + seasonal + noise

    demand_dir = os.path.join(BASE_DIR, "demand")
    os.makedirs(demand_dir, exist_ok=True)

    for day in range(days):
        start = day * MINUTES_PER_DAY
        end = start + MINUTES_PER_DAY
        np.savetxt(demand_path(day + 1), demand[start:end], fmt="%.2f", comments="")

    return days


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 86557
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 364
    created = generate_demand(seed, days)
    print(f"Created {created} demand files (seed={seed})")
