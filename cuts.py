import matplotlib.pyplot as plt

scenario_vec = [100, 1000, 5000, 7000, 10000,
                15000, 20000, 25000, 30000, 37000,
                45000, 50000, 60000, 70000, 75000,
                80000, 85000, 90000, 100000, 105000]

# Alg. 1
t_vec1 = [
    488.6, 3477.06666667, 4950.4, 5375.26666667, 3834.4,
    4053.93333333, 5332.4, 4504.8, 4113.13333333, 3779.53333333,
    5552.73333333, 4043.06666667, 5606.66666667, 4430.73333333,
    7070.13333333, 4160.33333333, 4105.06666667, 4320.26666667,
    4905.6, 4699.86666667
]

# Extensive
t_vec2 = [
    17716.46666667, 37612.13333333, 38242.33333333, 41498.33333333,
    33483.73333333, 35359.93333333, 43485.66666667, 36351.53333333,
    36065.26666667, 35365.6, 44159.06666667, 36865.6,
    45929.13333333, 39247.73333333, 55524.46666667, 37081.53333333,
    36964.6, 37364.73333333, 40912.86666667, 40308.8
]


# Stacked cut plots


fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(10,8),
    dpi=300,
    sharex=True
)


# Top plot (cb invocations)

ax1.plot(
    scenario_vec,
    t_vec2,
    marker='o',
    color='blue',
    linewidth=1.5
)

ax1.set_ylabel("Callback Invocations")
ax1.set_title("Average Callback Invocations by Scenario Count")

ax1.grid(True, linestyle='--', alpha=0.5)


# Bottom plot (number of cuts)


ax2.plot(
    scenario_vec,
    t_vec1,
    marker='s',
    color='lightblue',
    linewidth=1.5
)

ax2.set_xlabel("Number of scenarios")
ax2.set_ylabel("Cuts added")
ax2.set_title("Average Generated Cuts by Scenario Count")

ax2.grid(True, linestyle='--', alpha=0.5)

# -----------------------------------

plt.tight_layout()

plt.show()