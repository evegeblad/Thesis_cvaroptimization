 # Speciale_cvaroptimization
The repository contains the different scripts used for my thesis in operations research in the topic CVaR optmization. 

## Production planning problem - Variant 1
The following scripts contain the extensive model and the CVaR optimization Algorithm for the production planning problem Variant 1
  - pp_CB_alg1.py
  - extensive_variant1.py

Note that both Algorithm 1 and the extenisve model formulation has been tested in a for loop, and one need to decide to loop over different seeds or different instance sizes. When tested on 15  randomly selected seeds, the 15 seeds are

[74, 857, 163, 838, 93, 10, 653, 61, 268, 136, 907, 1, 645, 475, 21]


### Plots
The following scripts has been used for plotting results
  - avg_runtime_variant1.py
  - avgruntimelog_variant1.py
  - barplots.py
  - cuts.py (average cuts and cb invocations)
  
## Production planning problem - Variant 2
The following scripts contain the extensive model and the CVaR optimization Algorithm for the production planning problem Variant 2
  - Alg2_variant2.py (includes plots for single instances)
  - extensive_variant2.py

### Plots
The following scripts has been used for plotting results
- plots_runtime_variant2.py

Note that both Algorithm 2 and the extenisve model formulation has been tested in a for loop, and one need to decide to loop over different seeds or different instance sizes. When tested on 10  randomly selected seeds, the 10 seeds are

[27, 761, 32, 308, 489, 119, 50, 264, 885,1]

When tested on 5 different seeds these were: 

[27, 761, 32, 308,1]

And two different seeds: 

[32,1]

