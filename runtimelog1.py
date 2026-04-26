import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Scenario sizes
scenario_vec = [
    100, 1000, 5000, 10000, 15000, 25000, 50000, 60000, 65000, 70000,
    72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500,
    95000, 97500, 100000, 105000, 110000
]

# Convert to thousands for x-axis
scenario_k = [x  for x in scenario_vec]

# Algorithm 1
t_vec1 = [
    0.3808, 4.5666, 7.8193, 12.7015, 17.0121, 26.8048,
    54.5845, 61.3820, 65.2851, 78.6589, 92.8490, 69.3191,
    87.8558, 76.7099, 103.1865, 98.7929, 94.4299, 104.8869,
    87.6906, 108.7437, 95.5971, 103.7428, 99.2741, 122.9555
]

# Extensive model
t_vec2 = [
    0.0554, 0.6644, 5.6845, 13.1584, 21.2154, 41.1765,
    111.8170, 163.0651, 187.9743, 224.0023, 262.8331, 292.9804,
    353.8096, 369.3337, 337.3772, 360.9713, 411.8724, 476.9929,
    457.2554, 361.5146, 498.3052, 674.1400, 567.2319, 931.9755
]

# Figure
plt.figure(figsize=(10,6), dpi=300)

# Plot lines
plt.plot(scenario_k, t_vec1, marker='o',  label='Alg. 1', color = 'blue')
plt.plot(scenario_k, t_vec2, marker='s',  label='Extensive', color = 'lightblue')

# Log scale
plt.yscale('log')

# Labels
plt.xlabel("Number of Scenarios (K)")
plt.ylabel("Time (seconds, log scale)")
plt.title("Runtime Comparison")

# Legend
plt.legend()
plt.grid()


plt.show()