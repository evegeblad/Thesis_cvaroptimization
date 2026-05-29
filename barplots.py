#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import math


# 10,000 scenarios


run1_10k = [ 21.0149788 ,  40.5715499   ,43.5107369 ,  34.8860251 , 112.924886,
  49.4408544 ,  61.7328881  , 34.4191057 ,  43.7143925 ,  24.7096285,
  32.5296408  , 21.4216669 ,  18.7269411  , 24.4716915 ,  31.95792421]

run2_10k = [51.2950502, 59.2927025, 48.4200786 ,38.4176406, 37.8476397 ,38.5361678,
 40.4818575, 40.6218793, 51.7448595 ,45.8820803 ,42.8471068 ,41.3516527,
 41.0341303, 56.2438797, 80.8193135]

# 100,000 scenarios


run1_100k = [ 70.8060641,  102.327028 ,  160.391579 ,  116.602996  , 315.253041,
 186.25329  ,  540.9944    , 135.467126 ,  121.057057  ,  84.932833,
 107.578676  ,  94.8394875  , 83.5864755 ,  89.51533092 , 63.6341145 ]

run2_100k = [1002.50639279 , 563.59471921 , 716.29352208 , 514.56028942 , 491.62329171,
  545.54582429  ,646.40814413 , 662.31048046 , 507.86231417 , 597.28809117,
  494.57452288 , 564.53794696 , 528.47027742 , 607.164594 ,   841.707506  ]


# Common settings


instances = [rf"$I_{{{i}}}$" for i in range(1, 16)]

x = np.arange(len(instances))
width = 0.38

# Averages
avg_run1_10k = sum(run1_10k) / len(run1_10k)
avg_run2_10k = sum(run2_10k) / len(run2_10k)

avg_run1_100k = sum(run1_100k) / len(run1_100k)
avg_run2_100k = sum(run2_100k) / len(run2_100k)


# Create stacked subplots


fig, axes = plt.subplots(
    2, 1,
    figsize=(14, 10),
    dpi=300,
)
# Increase vertical spacing between plots
fig.subplots_adjust(hspace=1.60)

# Top plot: 30,000 scenarios


ax = axes[0]

ax.bar(x - width/2, run1_10k, width,
       label="Alg. 1", color="blue")

ax.bar(x + width/2, run2_10k, width,
       label="Extensive", color="lightblue")

# Average lines
ax.axhline(avg_run1_10k, color="blue",
           linestyle="--", linewidth=2,
           label="Alg. 1 Avg")

ax.axhline(avg_run2_10k, color="lightblue",
           linestyle="--", linewidth=2,
           label="Extensive Avg")

ax.set_ylabel("Runtime (sec)")
ax.set_title("Runtime Comparison (30,000 Scenarios)")

ax.set_xlabel("Instance")
ax.set_xticks(x)
ax.set_xticklabels(instances)

ax.grid(axis='y', linestyle=':', alpha=0.7)
ax.legend(framealpha=0.4)


#100,000 scenarios

ax = axes[1]

ax.bar(x - width/2, run1_100k, width,
       label="Alg. 1", color="blue")

ax.bar(x + width/2, run2_100k, width,
       label="Extensive", color="lightblue")

# Average lines
ax.axhline(avg_run1_100k, color="blue",
           linestyle="--", linewidth=2,
           label="Alg. 1 Avg")

ax.axhline(avg_run2_100k, color="lightblue",
           linestyle="--", linewidth=2,
           label="Extensive Avg")

ax.set_ylabel("Runtime (sec)")
ax.set_xlabel("Instance")
ax.set_title("Runtime Comparison (100,000 Scenarios)")

ax.set_xticks(x)
ax.set_xticklabels(instances)

ax.grid(axis='y', linestyle=':', alpha=0.7)
ax.legend(framealpha=0.4)

# Layout
plt.tight_layout(h_pad=2)

# Show plot
plt.show()