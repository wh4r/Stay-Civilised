import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt

# ----- IMPORTANT: TO DO -----
# The graph must extend for at least 364 cycles
# Remove random walk away from 1000
# Add another sin wave (0 < x < 4pi) for seasonal demand (demand peaks summer/winter)

# variables
c = 0
var = 100
noise = 150
integration_constant = 1000
seed = 86557


# --- Curve with noise ---
x = np.arange(0.0, 24*100, 0.5) 
y = np.sin((x / 24) * 2 * np.pi) * var + c

np.random.seed(seed)
noise = np.random.uniform(-noise, noise, size=len(y))
y_noisy = y + noise

points_to_add = 5
num_gaps = len(x) - 1
total_points = (num_gaps * (points_to_add + 1)) + 1

x_new = np.linspace(x.min(), x.max(), total_points)
spline = make_interp_spline(x, y_noisy, k=3)
y_new = spline(x_new)

# --- Integrated curve---
antiderivative_spline = spline.antiderivative()
y_integrated = antiderivative_spline(x_new) - antiderivative_spline(x.min()) + integration_constant

# --- Graphing ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
# top
ax1.scatter(x, y_noisy, color='red', s=20, zorder=3, label='Original Points')
ax1.plot(x_new, y_new, color='blue', linewidth=2, label='Curve')
ax1.plot(x, y, color='green', linestyle=':', alpha=0.7, label='Reference Sine Wave')
ax1.set_ylabel("Original Y Scale")
ax1.set_title("Curve")
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()
# bottom
ax2.plot(x_new, y_integrated, color='purple', linewidth=2.5, label=f'Integrated Line (C={integration_constant})')
ax2.set_xlabel("X")
ax2.set_ylabel("Integrated Cumulative Scale")
ax2.set_title("Integrated Curve")
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend()

plt.tight_layout()
plt.show()