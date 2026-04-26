#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 07:50:56 2026

@author: emmaviktoriaegeblad
"""

import matplotlib.pyplot as plt
import math


# Data
seeds = [74, 857, 163, 838, 93, 51, 653, 61, 268, 136, 907, 67, 645, 475, 21, 1, 10]

run1 = [130.40053879097104, 71.67780383303761, 105.02720483392477, 173.4453178329859, 125.17659616586752, 361.10001429193653, 196.8572673331946, 244.66348612494767, 611.749280750053, 148.88835754198954, 133.94313891697675, 93.70752316596918, 125.85456791706383, 111.42789762490429, 98.79657670808956, 103.70324945799075, 76.33262091688812]

run2 = [695.2068622910883, 928.7556469580159, 475.8841406251304, 633.3698331669439, 571.8676290828735, 546.1270101249684, 589.7544720838778, 863.0085757921916, 683.0107552499976, 700.476060874993, 468.60745487501845, 633.2812236249447, 506.74517583311535, 459.31862049992196, 810.6885154168122, 674.14, 737.009223583038]
data = sorted(zip(seeds, run1, run2))

# Unpack sorted data
seeds_sorted, run1_sorted, run2_sorted = zip(*data)

# Compute averages
avg_run1 = sum(run1) / len(run1)
avg_run2 = sum(run2) / len(run2)

std_run1 = math.sqrt(sum((x - avg_run1)**2 for x in run1) / len(run1))
std_run2 = math.sqrt(sum((x - avg_run2)**2 for x in run2) / len(run2))

# Plot
plt.figure(figsize=(10,6), dpi=300)

plt.plot(seeds_sorted, run1_sorted, label="Alg. 1", marker='o', color="blue")
plt.plot(seeds_sorted, run2_sorted, label="Extensive", marker='o', color="lightblue")

# Add average lines (dotted)
plt.axhline(avg_run1, color="blue", linestyle="--", label="Alg. 1 Avg")
plt.axhline(avg_run2, color="lightblue", linestyle="--", label="Extensive Avg")

plt.xlabel("Seed")
plt.ylabel("Runtime (sec)")
plt.title("Runtime vs Seed (100,000 scenarios)")

plt.legend(framealpha=0.4)
plt.grid()
plt.show()

print(avg_run1)
print(avg_run2)
print(std_run1)
print(std_run2)

