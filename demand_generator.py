import numpy as np
import matplotlib.pyplot as plt
import os
import platform

# -----------------------------
# variables
# -----------------------------
daily_amplitude = 100          # Daily demand variation
seasonal_amplitude = 60        # Seasonal demand variation
noise_amplitude =30            # Random noise
base_demand = 1000             # Average demand
seed = 86557                   # Replace with random number
days = 364

np.random.seed(seed)

# -----------------------------
# generate demand
# -----------------------------
minutes_per_day = 24 * 60
total_minutes = days * minutes_per_day

t = np.arange(total_minutes)
time_days = t / minutes_per_day

daily = daily_amplitude * np.cos(2 * np.pi * time_days - np.pi)
seasonal = seasonal_amplitude * np.sin(2 * np.pi * time_days / days)

noise = np.random.uniform(
    -noise_amplitude,
    noise_amplitude,
    total_minutes
)


demand = base_demand + daily + seasonal + noise

try:
    os.mkdir("demand")
except FileExistsError:
    print("Folder already exists.")

# -----------------------------
# save to file
# -----------------------------
for day in range(days):
    start = day * minutes_per_day
    end = start + minutes_per_day

    day_data = demand[start:end]

    filename = f"demand\\day_{day+1:03d}.txt" if platform.system()=="Windows" else f"demand/day_{day+1:03d}.txt" if platform.system()=="Darwin" else ""

    np.savetxt(
        filename,
        day_data,
        fmt="%.2f",
        comments=""
    )

print(f"Created {days} files")

plt.figure(figsize=(12,5))
plt.plot(demand[:minutes_per_day], color="blue")
plt.title("Electricity Demand - Day 1")
plt.xlabel("Minute of Day")
plt.ylabel("Demand")
plt.grid(True)
plt.tight_layout()
plt.show()