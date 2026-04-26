#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:56:56 2026

@author: emmaviktoriaegeblad
"""

import gurobipy as gp
import numpy as np
import random as r
import time


scenario_vec = [100, 1000, 5000, 10000, 15000, 25000, 50000, 60000, 65000, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500, 100000, 105000, 110000]
# [100, 1000, 5000, 10000, 15000, 25000, 50000, 60000, 65000, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500, 100000, 105000, 110000]

seed_vec = [74, 857, 163, 838, 93, 51, 653, 61, 268, 136, 907, 67, 645, 475, 21, 1, 10]

t_vec = [0.0] * len(scenario_vec)
obj_vec = [0.0] * len(scenario_vec)

for i in range(len(seed_vec)): 
    t_vec[i] = 0
    obj_vec[i] = 0


for i in range(len(scenario_vec)): 

    
    class ProductionPlanningProblem:
    
        def __init__(self,n_products:int, n_facilities:int, n_production_levels:int, instance_no:int=1):
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
    
     #change seed if needed. 
    
    n_products = 10
    n_facilities = 5
    n_prod_level = 3
    
    #10 products, 5 facilities and 3 production levels
    pp = ProductionPlanningProblem(10,5,3, instance_no=1)
    
    
    K = scenario_vec[i]
    C = pp.production_costs
    K_dict = pp.fixed_costs
    S = list(range(K))
    total_capacity = pp.total_capacity
    lower_bound = pp.lower_bound
    upper_bound = pp.upper_bound
    P = pp.full_price
    O = pp.discounted_price
    
    Y, D = pp.generate_sample(scenario_vec[i],sample_no=1)
    
    EPS = 1e-6
    
    alpha = 0.85
    
    pi = {s: 1.0/len(S) for s in S} 
    
    
    # Variables
    # ----------------------------
    
    x = m.addVars(n_products, n_facilities, lb=0.0)
    y = m.addVars(n_products, n_facilities, n_prod_level, vtype=gp.GRB.BINARY)
    
    
    vartheta = m.addVar(lb=0.0)
    
    z = m.addVar(lb=-gp.GRB.INFINITY)
    
    
    # Constraints
    # ----------------------------
    
    m.addConstrs(gp.quicksum(x[p,f] for p in range(n_products))<= total_capacity[f] for f in range(n_facilities))
    
    m.addConstrs(gp.quicksum(y[p, f, l] for l in range(n_prod_level)) == 1
                for p in range(n_products) for f in range(n_facilities))
    
    m.addConstrs(gp.quicksum(lower_bound[p, f, l] * y[p, f, l] for l in range(n_prod_level)) <= x[p, f]
                for p in range(n_products) for f in range(n_facilities))
    m.addConstrs(gp.quicksum(upper_bound[p, f, l] * y[p, f, l] for l in range(n_prod_level)) >= x[p, f]
                for p in range(n_products) for f in range(n_facilities))
    
    
    # Objective
    # ----------------------------
   #First stage costs
    cost_expr = gp.quicksum(C[p, f] * x[p, f] for p in range(n_products) for f in range(n_facilities)) + \
                gp.quicksum(K_dict[p, f, l] * y[p, f, l] for p in range(n_products) for f in range(n_facilities) for l in range(n_prod_level))
    
    
    m.setObjective(cost_expr+z+1/(1-alpha)*vartheta)

    
    
    def scenario_revenue_expr(s, x_val):
        expr = 0
        for p in range(n_products):
            q_val = sum(Y[p, f, s] * x_val[p, f] for f in range(n_facilities))
    
            if D[p, s] >= q_val:
                expr += P[p] * gp.quicksum(Y[p, f, s] * x[p, f] for f in range(n_facilities))
            else:
                expr += (
                    O[p] * gp.quicksum(Y[p, f, s] * x[p, f] for f in range(n_facilities))
                    + (P[p] - O[p]) * D[p, s]
                )
        return expr

    
    def add_cut_initial(subset, x_val):
        expr = gp.quicksum(
            pi[s] * (-scenario_revenue_expr(s, x_val) - z)
            for s in subset
        )
        m.addConstr(expr <= vartheta)
    
    
    #To store D and Y in array instead, which is fasdter with numpy
    Y_arr = np.zeros((K, n_products, n_facilities), dtype=float)
    D_arr = np.zeros((K, n_products), dtype=float)
    
    for s in range(K):
        for p in range(n_products):
            D_arr[s, p] = D[p, s]
            for f in range(n_facilities):
                Y_arr[s, p, f] = Y[p, f, s]
    
    
    #attach variables and parameters to the model, so they can be called in callback
    m._x = x
    m._z = z
    m._vartheta = vartheta
    m._P = n_products
    m._F = n_facilities
    m._K = K
    m._Y = Y_arr
    m._D = D_arr
    m._Pprice = np.array([P[p] for p in range(n_products)], dtype=float)
    m._Oprice = np.array([O[p] for p in range(n_products)], dtype=float)
    m._PmO = m._Pprice - m._Oprice
    
    m._block = 128 #Block size in loop
    m._eps_tail = 1.0 
    m._tol_violation = 1.0 
    m._tau_mass = 1e-6
    m._tau_const = 1e-6
    m._tau_coef = 1e-6
    
    m._cut_count = 0
    m._debug_log = []  
    m._callback_calls = 0
    

    # Callback for solving algorithm 1
    
    t0 = time.perf_counter() # To calculate runtime
    
    def callback(model, where):
        if where != gp.GRB.Callback.MIPSOL:
            return
    
        model._callback_calls += 1
    
        xV = model.cbGetSolution(model._x)
        zV = model.cbGetSolution(model._z)
        thV = model.cbGetSolution(model._vartheta)
    
        Pn = model._P
        Fn = model._F
        K = model._K
    
        #store x in a matrix for P and F
        x_mat = np.empty((Pn, Fn), dtype=np.float64)
        for p in range(Pn):
            for f in range(Fn):
                x_mat[p, f] = xV[p, f]
    
        #get prices for second stage
        Pprice = model._Pprice
        Oprice = model._Oprice
        
        #diff between P and O
        PmO = model._PmO
    
        #To be used for the cut generation
        coeff = np.zeros((Pn, Fn), dtype=np.float64)
        const_term = 0.0
        prob_mass = 0.0
        lhs = 0.0
    
        block = model._block

        
        #handle scenarios in blocks instead of all at once
        for start in range(0, K, block):
            end = min(start + block, K)
            
            #Yield and demand in current block
            Y_blk = model._Y[start:end, :, :]   # (b,P,F)
            D_blk = model._D[start:end, :]      # (b,P)
    
            #vector product
            q_blk = np.einsum( 'bpf,pf->bp', Y_blk, x_mat)
            
            #true/false
            demand_met = (D_blk >= q_blk)
    
    
            #revenue depending on where demand is met in block
            rev_bp = np.where(
                demand_met,
                Pprice[None, :] * q_blk,
                Oprice[None, :] * q_blk + PmO[None, :] * D_blk
            )
            
            #Scenario loss in block
            loss_b = -rev_bp.sum(axis=1)
            w_b = loss_b - zV
            
            #tail: where losses exceed threshold value z
            tail = (w_b > model._eps_tail)
            
            
            #If no loss from a scenario in the block is greater than z, then continue to next block
            if not np.any(tail):
                continue
    
            #Tail mass probabilities
            tail_count = np.count_nonzero(tail)
            prob_mass += tail_count / K
            lhs += w_b[tail].sum() / K
            
            
            price_bp = np.where(demand_met, Pprice[None, :], Oprice[None, :])
            coeff += -(price_bp[tail, :, None] * Y_blk[tail, :, :]).sum(axis=0) / K
    
            const_bp = np.where(demand_met, 0.0, -PmO[None, :] * D_blk)
            const_term += const_bp[tail, :].sum() / K
    
        
        violated = lhs > thV + model._tol_violation

        if not violated:
            return
    
        
        
        #add cut if needed
        expr = gp.LinExpr(const_term)
        for p in range(Pn):
            for f in range(Fn):
                c = coeff[p, f]
                if abs(c) > 1e-15:
                    expr.addTerms(c, model._x[p, f])
        expr.addTerms(-prob_mass, model._z)
    
        model.cbLazy(expr <= model._vartheta)
        
        model._cut_count+=1
    
    
    #initialization
    x_zero = {(p, f): 0.0 for p in range(n_products) for f in range(n_facilities)}
    S_hat_1 = tuple(S)
    add_cut_initial(S_hat_1, x_zero)
    m.Params.PreCrush = 1
    m.Params.LazyConstraints = 1
    m._cut_count = 0
    m.optimize(callback)
    t_total = time.perf_counter() - t0
    
    print("Number of callback calls:", m._callback_calls)
    print("Number of lazy cuts added:", m._cut_count)

    
    #print(f"Total elapsed time (solver + Python): {t_total:.2f} seconds")
    objectV = m.ObjVal
    
    
    t_vec[i] = t_total
    obj_vec[i] = objectV
    
    print(i)


print(t_vec)
print(obj_vec)

gp.disposeDefaultEnv()