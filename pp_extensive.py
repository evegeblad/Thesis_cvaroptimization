import gurobipy as gp
import numpy as np
import random as r
import time


scenario_vec = [100, 1000, 5000, 10000, 15000, 25000, 50000, 60000, 65000, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500, 100000, 105000, 110000]
# , 10000, 15000, 25000, 50000, 60000, 65000, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500, 100000, 105000, 110000

t_vec = [0.0] * len(scenario_vec)
obj_vec = [0.0] * len(scenario_vec)

for i in range(1): 
    t_vec[i] = 0
    obj_vec[i] = 0

np.random.seed(907)

for i in range(1): 
    class ProductionPlanningProblem:
        
            def __init__(self,n_products:int, n_facilities:int, n_production_levels:int, instance_no:int=10):
              '''
              The constructor generates a random instance of the problem.
              The instance number acts as the seed for the random number generator (default 1).
              This allows you to generate the same instance multiple times.
              To generate a different instance of the same size you simply change the instance number.
              '''
              r.seed(instance_no)
        
              self.n_facilities = n_facilities
              self.n_products = n_products
              self.n_production_levels = n_production_levels
        
              self.production_costs = {(p,f): 40 + r.random() * 60 for p in range(n_products) for f in range(n_facilities)}
              self.fixed_costs = {(p,f,l): r.randint(200,400) * l for p in range(n_products) for f in range(n_facilities) for l in range(n_production_levels)}
              self.full_price = {p : 140 + r.random() * 40 for p in range(n_products)}
              self.discounted_price = {p : 15 + r.random() * 25 for p in range(n_products)}
              self.total_capacity = {f : r.randint(3000,5000) *self.n_products for f in range(n_facilities)}
              self.upper_bound = {(p,f,l): (self.total_capacity[f]/self.n_products) * (l+1)/n_production_levels for p in range(n_products) for f in range(n_facilities) for l in range(n_production_levels) }
              self.lower_bound = {(p,f,l): 0 if l == 0 else self.upper_bound[p,f,l-1]+1 for p in range(n_products) for f in range(n_facilities) for l in range(n_production_levels) }
        
            def generate_sample(self, sample_size:int, sample_no:int=1):
              '''
              This method generates an iid sample of yield and demand from the underlying distributions.
              sample_size: number of samples (K in the notation of the lecture note)
              sample_no: seed for the random number generator. This allows you to generate the same sample multiple times. You may change this number to generate different samples (e.g., if you need M repetitions).
              '''
              np.random.seed(sample_no)
              yeld = {(p,f,s): np.random.triangular(0.85,0.95,1) for p in range(self.n_products) for f in range(self.n_facilities) for s in range(sample_size)}
              demand = {(p,s): np.random.triangular(2000,4000,6000) for p in range(self.n_products) for s in range(sample_size)}
              return yeld, demand
        


    # Data
    # ----------------------------
    
    m = gp.Model()
    
    
    n_products = 10
    n_facilities = 5
    n_prod_level = 3
    
    #10 products, 5 facilities and 3 production levels
    pp = ProductionPlanningProblem(10,5,3, instance_no=268)
    
    
    K = 85000
    C = pp.production_costs
    K_dict = pp.fixed_costs
    S = list(range(K))
    total_capacity = pp.total_capacity
    lower_bound = pp.lower_bound
    upper_bound = pp.upper_bound
    P = pp.full_price
    O = pp.discounted_price
    
    Y, D = pp.generate_sample(85000,268)
    
    alpha = 0.85
    
    pi = {s: 1.0/len(S) for s in S} 
    
    seen_cuts = set()
    
    
    #Variables
    x = m.addVars(n_products, n_facilities, lb=0.0)
    y = m.addVars(n_products, n_facilities, n_prod_level, vtype=gp.GRB.BINARY)
    w = m.addVars(n_products, S, lb=0.0)
    o = m.addVars(n_products, S, lb=0.0)
    z = m.addVar(lb=-gp.GRB.INFINITY)
    vs =  m.addVars(S, lb=0)
     
    
    #constraints
    
    m.addConstrs(gp.quicksum(x[p,f] for p in range(n_products))<= total_capacity[f] for f in range(n_facilities))
    
    m.addConstrs(gp.quicksum(y[p, f, l] for l in range(n_prod_level)) == 1
                for p in range(n_products) for f in range(n_facilities))
    
    m.addConstrs(gp.quicksum(lower_bound[p, f, l] * y[p, f, l] for l in range(n_prod_level)) <= x[p, f]
                for p in range(n_products) for f in range(n_facilities))
    m.addConstrs(gp.quicksum(upper_bound[p, f, l] * y[p, f, l] for l in range(n_prod_level)) >= x[p, f]
                for p in range(n_products) for f in range(n_facilities))
    
    m.addConstrs(w[p, s] + o[p, s] == 
                 gp.quicksum(Y[p, f, s] * x[p, f] for f in range(n_facilities)) for p in range(n_products) for s in S)
    
    
    m.addConstrs(w[p,s] <= D[p,s] for p in range(n_products) for s in S)
    
    cost_expr = gp.quicksum(C[p, f] * x[p, f] for p in range(n_products) for f in range(n_facilities)) + \
                gp.quicksum(K_dict[p, f, l] * y[p, f, l] for p in range(n_products) for f in range(n_facilities) for l in range(n_prod_level))
    
    
    def scenario_revenue(s):
        return gp.quicksum(P[p]*w[p,s] + O[p]*o[p,s] for p in range(n_products))
    
    vUpperBound = {s: m.addConstr(vs[s] >= - scenario_revenue(s) - z) for s in S }
    
    
    m.setObjective(cost_expr+z+1/(1-alpha)*gp.quicksum(pi[s]*vs[s] for s in S))
    
    t0 = time.perf_counter()
    
    m.optimize()
    
    t_total = time.perf_counter() - t0
    print(f"Total elapsed time (solver + Python): {t_total:.2f} seconds")
    
    objectV = m.ObjVal
    
    
    t_vec[i] = t_total
    obj_vec[i] = objectV


print(t_vec)
print(obj_vec)
    
    
