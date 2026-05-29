import matplotlib.pyplot as plt

# Scenario sizes
scenario_vec = [100, 1000, 5000, 7000, 10000, 
                15000, 20000, 25000, 30000, 37000, 
                45000, 50000, 60000, 70000, 75000, 
                80000,  85000, 90000,  100000, 105000]

# First run 
t_vec1 = [  0.37971577,   4.31897204,  17.2860398,   23.65652206,  16.3245659,
  22.13980888 , 45.76614491 , 38.01301655 , 39.73552736 , 44.17289773,
  83.9054614  , 62.92292393 ,110.24998913 , 92.68330878 ,184.46281267,
 104.99059697 ,111.21127128 ,122.21616553 ,151.5492999 , 149.95380245]

# Second run (your new data)
t_vec2 = [3.58890584e-02 ,2.52046244e-01 ,3.38255002e+00, 5.07481075e+00,
 1.02674179e+01 ,2.29531695e+01 ,3.08455060e+01 ,6.59849046e+01,
 4.76557359e+01, 8.78158948e+01 ,1.40669450e+02 ,1.39941534e+02,
 1.67033608e+02, 2.56801810e+02 ,3.39941554e+02 ,4.03422604e+02,
 4.55936791e+02, 4.66962808e+02, 6.18963194e+02 ,6.19168136e+02]

# Plot both
# Figure
plt.figure(figsize=(10,6), dpi=300)
plt.plot(scenario_vec, t_vec1, marker='o', label='Alg. 1', color = 'blue')
plt.plot(scenario_vec, t_vec2, marker='s', label='Extensive',  color = 'lightblue')

# Labels
plt.xlabel("Number of Scenarios (K)")
plt.ylabel("Time (seconds)")
plt.title("Average Runtime Comparison")

# Legend + grid
plt.legend()
plt.grid()

# Optional: log scale (highly recommended here)
# plt.yscale('log')

plt.show()