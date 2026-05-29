#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 18:46:12 2026

@author: emmaviktoriaegeblad
"""

import matplotlib.pyplot as plt

# Data
scenarios = [100, 1000, 3000, 5000, 7000, 10000, 16000, 20000, 27000, 30000]

algorithm2 = [
    6.49,
    79.32,
    935.25,
    3964.11,
    9520.71,
    6389.27,
    9580.00,
    10417.17,
    23212.55,
    31264.96
]

# Extensive model has no runtime for 37,000 scenarios
extensive_model_scenarios = [100, 1000, 3000, 5000, 7000, 10000, 16000, 20000, 27000, 30000]
extensive_model = [
    0.42,
    7.84,
    44.68,
    82.56,
    240.22,
    358.51,
    1154.37,
    2143.92,
    4563.81,
    6563.53
]

# Plot
plt.figure(figsize=(10, 6))

plt.plot(scenarios, algorithm2, marker='o', linewidth=2, label='Algorithm 2', color = 'blue')
plt.plot(extensive_model_scenarios, extensive_model,
         marker='s', linewidth=2, label='Extensive model', color = 'lightblue')

# Labels and title
plt.xlabel('Number of Scenarios (K)')
plt.ylabel('Runtime (seconds)')
plt.title('Average Runtime Comparison')

# Grid and legend
plt.grid(True)
plt.legend()

# remove if not logscale plot
plt.yscale('log')

plt.tight_layout()
plt.show()



