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

run1 = [14.78826120798476, 7.809710165951401, 8.420248624868691, 12.292422333965078, 10.102197624975815, 53.40990950004198, 17.711677917046472, 71.69968375004828, 21.58593170903623, 14.27921670791693, 15.956354249967262, 16.245511332992464, 13.634123916970566, 23.8300188339781, 15.22552541620098, 12.70, 15.488904915982857]

run2 = [14.677523416932672, 22.080492542125285, 8.303677374962717, 10.87193795805797, 10.101411999901757, 10.614389750175178, 8.89809887506999, 11.242263583932072, 9.582234000088647, 15.738019374897704, 9.735155417118222, 13.9540551668033, 9.577501999912784, 13.709036665968597, 12.648502917028964, 13.599659041967243, 19.681133833015338]
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
plt.title("Runtime vs Seed (10,000 scenarios)")

plt.legend(framealpha=0.4)
plt.grid()
plt.show()

print(avg_run1)
print(avg_run2)
print(std_run1)
print(std_run2)

