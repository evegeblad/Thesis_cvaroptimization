#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 17:48:55 2026

@author: emmaviktoriaegeblad
"""

import gurobipy as gp
import numpy as np
import random as r
import time #to compute time

seed_vec = [27, 761, 32, 308, 489, 119, 50, 264, 885, 1] #change seeds if wanted

scenario_vec = [100] #change for how many scenarios wanted

#vectors to store some data
t_vec = [0.0] * len(seed_vec)
cb_t_vec = [0.0] * len(seed_vec)
obj_vec = [0.0] * len(seed_vec)
cb_calls_vec = [0.0] * len(seed_vec)

for i in range(len(seed_vec)): 

    

    #parameter generation
    class ProductionPlanningProblem:
    
        def __init__(self,n_products:int, n_facilities:int, n_production_levels:int, n_locations:int,instance_no:int=1):
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
          self.n_locations = n_locations
    
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
          demand = {(p,q,s): np.random.triangular(2000,4000,6000) for p in range(self.n_products) for q in range(self.n_locations)
                    for s in range(sample_size)}
          return yeld, demand
    
    
    
    #data
    class Data:
        def __init__(self, pp: ProductionPlanningProblem, K: int, sample_no: int = 1):
            self.n_products = pp.n_products
            self.n_facilities = pp.n_facilities
            self.n_production_levels = pp.n_production_levels
            self.n_locations = pp.n_locations
            self.scenarios = K
    
            # first-stage data
            self.C = pp.production_costs
            self.K_dict = pp.fixed_costs
            self.total_capacity = pp.total_capacity
            self.lower_bound = pp.lower_bound
            self.upper_bound = pp.upper_bound
    
            # prices
            self.P = pp.full_price
            self.O = pp.discounted_price
    
            # sample
            self.Y, self.D = pp.generate_sample(K, sample_no)
    
            # scenario probabilities
            self.prob = 1.0 / K
    
            # transportation costs
            min_price = min(self.P[p] for p in range(self.n_products))
            self.H = {
                (f, q): r.uniform(0.1 * min_price, 0.9 * min_price)
                for f in range(self.n_facilities)
                for q in range(self.n_locations)
            }
    
    
    
    #master problem 
    def build_master(data: Data, alpha: float):
        m = gp.Model("master_cvar_lshape")
    
        P = range(data.n_products)
        F = range(data.n_facilities)
        L = range(data.n_production_levels)
        S = range(data.scenarios)
    
        # Safe lower bound for losses
        loss_lb = -sum(
            max(data.P[p], data.O[p]) *
            sum(data.upper_bound[p, f, data.n_production_levels - 1] for f in F)
            for p in P
        )
    
        # variables
        x = m.addVars(P, F, lb=0.0)
        y = m.addVars(P, F, L, vtype=gp.GRB.BINARY)
        mu = m.addVars(S, lb=loss_lb)
        z = m.addVar(lb=-gp.GRB.INFINITY)
        vartheta = m.addVar(lb=0.0)
    
        # capacity per facility
        m.addConstrs(
            (gp.quicksum(x[p, f] for p in P) <= data.total_capacity[f] for f in F)
        )
    
        # exactly one production level per (p,f)
        m.addConstrs(
            (gp.quicksum(y[p, f, l] for l in L) == 1 for p in P for f in F)
        )
    
        # lower / upper bounds implied by chosen level
        m.addConstrs(
            (
                gp.quicksum(data.lower_bound[p, f, l] * y[p, f, l] for l in L) <= x[p, f]
                for p in P for f in F
            )
        )
    
        m.addConstrs(
            (
                x[p, f] <= gp.quicksum(data.upper_bound[p, f, l] * y[p, f, l] for l in L)
                for p in P for f in F
            )
        )
    
        first_stage_cost = (
            gp.quicksum(data.C[p, f] * x[p, f] for p in P for f in F)
            + gp.quicksum(data.K_dict[p, f, l] * y[p, f, l] for p in P for f in F for l in L)
        )
    
        m.setObjective(
            first_stage_cost + z + (1.0 / (1.0 - alpha)) * vartheta,
            gp.GRB.MINIMIZE
        )
    
        # Initial aggregate CVaR cut.
        # Callback will add stronger subset cuts as needed.
        m.addConstr(
            gp.quicksum(data.prob * (mu[s] - z) for s in S) <= vartheta
        )
    
        # attach data to model
        m._x = x
        m._y = y
        m._mu = mu
        m._z = z
        m._vartheta = vartheta
        m._S = list(range(data.scenarios))
        m._pi = {s: data.prob for s in S}
        m._data = data
    
        return m
    
    #to compute duals of the second stage scenario losses
    
    class ScenarioLossDual:
        
        #initialization
        def __init__(self, data: Data, s: int):
            self.data = data
            self.s = s
    
            self.sp = gp.Model(f"dual_s_{s}")
            self.sp.Params.OutputFlag = 0
            self.sp.Params.Method = 1
    
            P = range(data.n_products)
            F = range(data.n_facilities)
            Q = range(data.n_locations)
    
            self.rho = self.sp.addVars(P, F, lb=-gp.GRB.INFINITY)
            self.lam = self.sp.addVars(P, Q, lb=0.0)
    
            self.sp.addConstrs(
                (
                    self.rho[p, f] + self.lam[p, q] >= data.P[p] - data.H[f, q]
                    for p in P for f in F for q in Q
                )
            )
    
            self.sp.addConstrs(
                (self.rho[p, f] >= data.O[p] for p in P for f in F)
            )
    
            # fixed scenario demand contribution
            for p in P:
                for q in Q:
                    self.lam[p, q].Obj = data.D[p, q, s]
    
            self.sp.update()
    
        #Solve dual subproblem
        def solve(self, xbar):
            P = range(self.data.n_products)
            F = range(self.data.n_facilities)
            Q = range(self.data.n_locations)
    
            # update x-dependent objective coefficients
            for p in P:
                for f in F:
                    self.rho[p, f].Obj = self.data.Y[p, f, self.s] * xbar[p, f]
    
            self.sp.optimize()
    
            if self.sp.Status != gp.GRB.OPTIMAL:
                raise RuntimeError(
                    f"Dual subproblem for scenario {self.s} not optimal. Status={self.sp.Status}"
                )
    
            revenue_s = self.sp.ObjVal
            loss_s = -revenue_s
    
            rho_val = np.empty((self.data.n_products, self.data.n_facilities))
            lam_val = np.empty((self.data.n_products, self.data.n_locations))
    
            for p in P:
                for f in F:
                    rho_val[p, f] = self.rho[p, f].X
    
            for p in P:
                for q in Q:
                    lam_val[p, q] = self.lam[p, q].X
    
            return loss_s, rho_val, lam_val
    
    
    
    def add_lshape_cut_lazy(model, s, rho, lam):
        data = model._data
        P = range(data.n_products)
        F = range(data.n_facilities)
        Q = range(data.n_locations)
    
        expr = gp.LinExpr()
    
        # constant term
        expr.addConstant(
            -sum(data.D[p, q, s] * lam[p, q] for p in P for q in Q)
        )
    
        # x-dependent term
        for p in P:
            for f in F:
                coeff = -data.Y[p, f, s] * rho[p, f]
                if abs(coeff) > 1e-4:
                    expr.addTerms(coeff, model._x[p, f])
    
        model.cbLazy(model._mu[s] >= expr)
    
    
    def add_cvar_subset_cut_lazy(model, S_star):
    
        expr = gp.LinExpr()
    
        total_pi = 0.0
        for s in S_star:
            expr.addTerms(model._pi[s], model._mu[s])
            total_pi += model._pi[s]
    
        expr.addTerms(-total_pi, model._z)
    
        model.cbLazy(model._vartheta >= expr)
        
    
    def get_dual(model, s):
        if s not in model._duals:
            model._duals[s] = ScenarioLossDual(model._data, s)
        return model._duals[s]
    
    
    def add_lshape_cut_static(model, s, rho, lam):
        data = model._data
        P = range(data.n_products)
        F = range(data.n_facilities)
        Q = range(data.n_locations)
    
        expr = gp.LinExpr()
    
        expr.addConstant(
            -sum(data.D[p, q, s] * lam[p, q] for p in P for q in Q)
        )
    
        for p in P:
            for f in F:
                coeff = -data.Y[p, f, s] * rho[p, f]
                if abs(coeff) > 1e-4:
                    expr.addTerms(coeff, model._x[p, f])
    
        model.addConstr(model._mu[s] >= expr)
    
    
    
    #callback
    def cvar_lshape_callback_blocked(model, where):
        model._callback_calls += 1
    
        if where != gp.GRB.Callback.MIPSOL:
            return
        
        model._mipsol_calls += 1
        model._sep_iter += 1

        nodecnt = int(model.cbGet(gp.GRB.Callback.MIPSOL_NODCNT))
        objbst = model.cbGet(gp.GRB.Callback.MIPSOL_OBJ)
        objbnd = model.cbGet(gp.GRB.Callback.MIPSOL_OBJBND)

        if model._mipsol_calls % 20 == 0:
            print(
                f"MIPSOL {model._mipsol_calls}, "
                f"node={nodecnt}, "
                f"best={objbst:.2f}, "
                f"bound={objbnd:.2f}"
                )
        
        model._cut_node.append(nodecnt)
        
        eps = model._eps
        block_size = getattr(model, "_block_size", 20)
        max_lshape_cuts = getattr(model, "_max_lshape_cuts", 50)
    
        t_iter = time.perf_counter()
        
    
        xV = model.cbGetSolution(model._x)
        muV = model.cbGetSolution(model._mu)
        zV = model.cbGetSolution(model._z)
        thV = model.cbGetSolution(model._vartheta)
    
        total_checked = 0
        total_cuts = 0
        subproblem_time = 0.0
        lshape_cuts_this_iter = 0
        cvar_cuts_this_iter = 0
    
        S_cb = model._S
        
        offset = (model._sep_iter * block_size) % len(S_cb)
        S_ordered = S_cb[offset:] + S_cb[:offset]
    
        # Step 1: L-shaped separation in blocks
        for start in range(0, len(S_ordered), block_size):
            end = min(start + block_size, len(S_ordered))
            S_block = S_ordered[start:end]
    
            block_violations = []
    
            for s in S_block:
                t_sp = time.perf_counter()
                loss_s, rho_s, lam_s = get_dual(model, s).solve(xV)
                subproblem_time += time.perf_counter() - t_sp
    
                total_checked += 1
    
                if muV[s] < loss_s - eps:
                    block_violations.append((s, rho_s, lam_s))
    
            # Add cuts after each block
            for s, rho_s, lam_s in block_violations:
                add_lshape_cut_lazy(model, s, rho_s, lam_s)
                total_cuts += 1
                lshape_cuts_this_iter += 1
                model._total_lshape_cuts += 1
                model._total_lazy_cuts += 1
    
                if total_cuts >= max_lshape_cuts:
                    break
    
            if total_cuts >= max_lshape_cuts:
                break
    
        # Step 2: CVaR subset separation
        S_star = [s for s in S_cb if muV[s] - zV > eps]
    
        cvar_cut_added = 0
    
        if S_star:
            lhs = sum(model._pi[s] * (muV[s] - zV) for s in S_star)
    
            if lhs > thV + eps:
                add_cvar_subset_cut_lazy(model, S_star)
                cvar_cut_added = 1
                cvar_cuts_this_iter = 1
                model._total_cvar_cuts += 1
                model._total_lazy_cuts += 1
    
        elapsed = time.perf_counter() - t_iter
    
        
        model._timing_rows.append({
            "iter": model._sep_iter,
            "node": nodecnt,
            "cuts_added": total_cuts + cvar_cut_added,
            "elapsed_sec": elapsed,
            "subproblem_sec_total": subproblem_time,
        })
        
        runtime_now = time.perf_counter() - model._run_start_time
    
        model._cut_runtime.append(runtime_now)
        model._cut_cum_total.append(model._total_lazy_cuts)
        model._cut_cum_lshape.append(model._total_lshape_cuts)
        model._cut_cum_cvar.append(model._total_cvar_cuts)
        model._cuts_this_iter.append(lshape_cuts_this_iter + cvar_cuts_this_iter)
    
    
    
    #to measure time spent in callback
    def timed_callback(model, where):
        t_cb = time.perf_counter()
        try:
            cvar_lshape_callback_blocked(model, where)
        finally:
            model._callback_time_total += time.perf_counter() - t_cb
    
    
    if __name__ == "__main__":
        n_products = 10
        n_facilities = 5
        n_prod_level = 3
        n_locations = 4
        K = scenario_vec[0]
        alpha = 0.85
    
        pp = ProductionPlanningProblem(
            n_products=n_products,
            n_facilities=n_facilities,
            n_production_levels=n_prod_level,
            n_locations=n_locations,
            instance_no=seed_vec[i],
        )
    
        data = Data(pp, K, sample_no=seed_vec[i])
    
        t0 = time.perf_counter()
    
        m = build_master(data, alpha)
        m.Params.PreCrush = 1
        m.Params.LazyConstraints = 1
        m.Params.MIPFocus = 1
        m.Params.Threads = 1
        
        
        m._eps = 1.0
        m._sep_iter = 0
        m._timing_rows = []
        m._hot_scenarios = []
        m._callback_calls = 0
        m._mipsol_calls = 0
        m._duals = {}
        
        
        m._duals = {s: ScenarioLossDual(data, s) for s in range(data.scenarios)}
    
        # initialization
        x0 = {}
        for p in range(data.n_products):
            for f in range(data.n_facilities):
                x0[p, f] = data.lower_bound[p, f, 0]
    
        # generate initial cuts
        losses = {}
    
        initial_cut_count =int(K)
    
        loss_records = []
        
        for s in range(data.scenarios):
            loss_s, rho_s, lam_s = m._duals[s].solve(x0)
            losses[s] = loss_s
            loss_records.append((loss_s, s, rho_s, lam_s))
            m._mu[s].Start = loss_s
        
        loss_records.sort(reverse=True)
    
        for loss_s, s, rho_s, lam_s in loss_records[:initial_cut_count]:
            add_lshape_cut_static(m, s, rho_s, lam_s)
    
        z0 = np.quantile(list(losses.values()), alpha)
        theta0 = sum(data.prob * max(losses[s] - z0, 0.0) for s in range(data.scenarios))
    
        m._z.Start = z0
        m._vartheta.Start = theta0
        
        #arrays to store data
        m._callback_time_total = 0.0 #to comupute runtime
        
        m._run_start_time = time.perf_counter()
    
        m._cut_runtime = []
        m._cut_cum_total = []
        m._cut_cum_lshape = []
        m._cut_cum_cvar = []
        m._cut_node = []
        m._cuts_this_iter = []
        
        
        m._total_lshape_cuts = 0
        m._total_cvar_cuts = 0
        m._total_lazy_cuts = 0
    
        t_opt_start = time.perf_counter()
        
        
        #___________optimize______________________
        m.optimize(timed_callback)
        t_opt = time.perf_counter() - t_opt_start
        
        t_total = time.perf_counter() - t0
        
        m._run_start_time = time.perf_counter()
    
        m._total_lshape_cuts = 0
        m._total_cvar_cuts = 0
        m._total_lazy_cuts = 0
        
        m._cut_progress_rows = []
        
        total_checked = 0
        total_cuts = 0
        subproblem_time = 0.0
        
        lshape_cuts_this_iter = 0
        cvar_cuts_this_iter = 0
        
        
        #_________________________plots___________________________
        #plots used to consider solution process (outcomment if unwanted):  
        
        import matplotlib.pyplot as plt
    
        plt.figure()
        plt.plot(m._cut_runtime, m._cut_cum_total, label="Total cuts", color = 'darkblue')
        plt.plot(m._cut_runtime, m._cut_cum_lshape, label="L-shaped cuts", color = 'lightblue')
        plt.plot(m._cut_runtime, m._cut_cum_cvar, label="CVaR cuts", color = 'blue')
        
        plt.xlabel("Runtime (seconds)")
        plt.ylabel("Cumulative cuts")
        plt.title("Growth of L-shaped and CVaR Cuts over Runtime (7000 Scenarios)")
        plt.legend()
        plt.grid(True)
        plt.show()
        
        plt.figure()
    
        plt.plot(m._cut_runtime, m._cuts_this_iter, color = 'blue')
        
        plt.xlabel("Runtime (seconds)")
        plt.ylabel("Cuts added per callback")
        plt.title("Cut generation intensity over runtime (7000 scenarios)")
        plt.grid(True)
        plt.show()
        
        iters = [row["iter"] for row in m._timing_rows]
        elapsed = [row["elapsed_sec"] for row in m._timing_rows]
        subproblem = [row["subproblem_sec_total"] for row in m._timing_rows]
        
        plt.figure()
        plt.plot(iters, elapsed, label="Total callback time per iteration", color = 'blue')
        
        plt.xlabel("Callback iteration")
        plt.ylabel("Runtime (seconds)")
        plt.title("Runtime per callback iteration")
        plt.legend()
        plt.grid()
        plt.show()
            
        runtime = np.array(m._cut_runtime)
        cuts = np.array(m._cuts_this_iter)
    
        # Keep only the last 100 seconds
        start_time = runtime[-1] - 50
    
        mask = runtime >= start_time
    
        plt.figure()
    
        plt.plot(runtime[mask], cuts[mask], color = 'blue')
    
        plt.xlabel("Runtime (seconds)")
        plt.ylabel("Cuts added per callback")
        plt.title("Cut generation intensity over last 50 seconds")
        plt.grid()
    
        plt.show()

        from collections import Counter
        
        # Extract node numbers
        nodes = [row["node"] for row in m._timing_rows]
        
        # Count callbacks per node
        node_counts = Counter(nodes)
        
        # Sort by node number
        x = sorted(node_counts.keys())
        y = [node_counts[n] for n in x]
        
        plt.figure()
        
        plt.bar(x, y, color = 'blue')
        
        plt.xlabel("Branch-and-bound node")
        plt.ylabel("Number of callback invocations")
        plt.title("Callback invocations per branch-and-bound node")
        
        plt.grid()
        plt.show()
        
        nodes = [row["node"] for row in m._timing_rows]
        iters = [row["iter"] for row in m._timing_rows]
        
        plt.figure()
        
        plt.plot(iters, nodes, color = 'blue')
        
        plt.xlabel("Callback iteration")
        plt.ylabel("Branch-and-bound node")
        plt.title("Branch-and-bound node over callback iterations")
        
        plt.grid()
        plt.figure()

        plt.plot(m._cut_node, m._cut_cum_total)
        
        plt.xlabel("Branch-and-bound node")
        plt.ylabel("Cumulative lazy constraints")
        plt.title("Growth of lazy constraints across branch-and-bound nodes")
        
        plt.grid()
        plt.show()
        
        plt.grid(True)
        plt.show()
        
    
        print(f"Total elapsed time: {t_total:.2f} seconds")
        print(f"Status: {m.Status}")
        print(f"SolCount: {m.SolCount}")
        
        print(f"Callback calls: {m._callback_calls}")
        print(f"MIPSOL calls: {m._mipsol_calls}")
        print(f"Timing rows: {len(m._timing_rows)}")
        
        print(f"Total callback time: {m._callback_time_total:.2f} seconds")
    
        if t_total > 0:
            print(f"Optimization wall time: {t_opt:.2f} seconds")
            print(f"Gurobi Runtime: {m.Runtime:.2f} seconds")
            print(f"Callback time: {m._callback_time_total:.2f} seconds")
            print(f"Callback share of optimization wall time: {100*m._callback_time_total/t_opt:.2f}%")
    
        if m.SolCount > 0:
            print(f"Objective value: {m.ObjVal:.6f}")
            print(f"z = {m._z.X:.6f}")
            print(f"theta = {m._vartheta.X:.6f}")
    
            # optional: inspect a few values
            for s in range(min(5, data.scenarios)):
                print(f"mu[{s}] = {m._mu[s].X:.6f}")
                
        t_vec[i] = t_total
        cb_t_vec[i] = m._callback_time_total
        obj_vec[i] = m.ObjVal
        cb_calls_vec[i] = m._callback_calls
        print(m._callback_calls)
        print(i)
        
#avg_runtime = sum(t_vec[i] for i in range(len(seed_vec)))/len(seed_vec)
#print(f"avg_runtime: {avg_runtime}")
#avg_cb_time = sum(cb_t_vec[i] for i in range(len(seed_vec)))/len(seed_vec)
#print(f"avg_cb_runtime: {avg_cb_time}")   

#avg_cb_calls = sum(cb_calls_vec[i] for i in range(len(seed_vec)))/len(seed_vec)
#print(f"avg_cb_calls: {avg_cb_calls}")   

#print some data

print(t_vec)
print(cb_t_vec)
print(obj_vec)
print(cb_calls_vec)
           
