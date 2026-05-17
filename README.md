# Speciale_cvaroptimization
The repository contains the different scripts used for my thesis in operations research in the topic CVaR optmization. 

## Production planning problem 
The following scripts contain the extensive model and the CVaR optimization Algorithm for the production planning problem 
  - pp_CB_alg1.py
  - pp_extensive.py

Note that both Algorithm 1 and the extenisve model formulation has been tested in a for loop, and one need to decide to loop over different seeds or different instance sizes. When tested on 15  randomly selected seeds, the 15 seeds are
$$seeds = [74, 857, 163, 838, 93, 51, 653, 61, 268, 136, 907, 67, 645, 475, 21]$$


### Plots
The following scripts has been used for plotting results
  - runtimelog1.py (log scale runtime plot for seed 1 results)
  - runtimelog10.py (log scale runtime plot for seed 10 results)
  - scatter_test10.py (scatterplot of runtime for different seeds at 10,000 scenarios)
  - scatter_test100.py (scatterplot of runtime for different seeds at 10,000 scenarios)
  - runtime 1
  - runtime 10
  - obj 1

  
## Production planning problem extension

