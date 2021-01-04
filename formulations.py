import gurobipy as grb
import tools
from bisect import bisect_left
import sys
import time
import functools
import csv
from math import comb

def timeis(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            start=time.time()
            func(*args, **kwargs)
            end=time.time()
            timer=end-start
            sys.stderr.write(" %s %.2f " %(func.__name__, timer))
        return inner
            
class formulation:

    G = 0
    model = 0
    x = []
    y = []
    z = 0
    name = 0

    def __init__(self, graph):
        self.threshold = 10000000 
        self.name = graph.split(".")[0]
        self.G = tools.Graph(inputfile=graph)
        
        self.G.degOrdering()
        

        self.model = grb.Model()
        self.model.setAttr("ModelSense", -1)
        
    
    def solveGurobi(self):
        with open("resultsforclique.csv",'a',newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            #add a header to csv file- uncomment when the code run for singel instance 
            #fields = ['Model','Graph name','n','m','d','g','Solve Status','#Nonzero','#B&B Nodes','LB','UB',"Solve Time"]
            #csvwriter.writerow(fields)

            for v in self.x:
                v.vtype = grb.GRB.BINARY
                
            for v in self.y:
                v.vtype = grb.GRB.BINARY
                
            self.model.Params.OutputFlag = 1
            
            startSolving=time.time()
            self.model.optimize()
            endSolving=time.time()
            solveTime=endSolving-startSolving
            sys.stderr.write("%.2f "%solveTime)
            
    
            for v in self.x:#what is this for?
                v.vtype = grb.GRB.CONTINUOUS   #what is this for?
    
            for v in self.y:    
                v.vtype = grb.GRB.CONTINUOUS
            
            status = self.model.getAttr(grb.GRB.Attr.Status)
            nonzerosCount = self.model.getAttr(grb.GRB.Attr.NumNZs)
            LPbound = self.model.getAttr(grb.GRB.Attr.ObjBound)
            BBNodeCount = self.model.getAttr(grb.GRB.Attr.NodeCount) 
            
            #uncomment for test
            #print("status:",status, "Node count: ",BBNodeCount,"LPbound: ",LPbound,"SolCount: ", self.model.getAttr(grb.GRB.Attr.SolCount) )
    		
            
            if self.model.getAttr(grb.GRB.Attr.Status) == 2:
                fields = [self.model.modelname, self.name, self.G.n, self.G.m, self.G.d,
                          self.G.d+1-self.model.getAttr(grb.GRB.Attr.ObjVal),status,
                          nonzerosCount, BBNodeCount ,
                          self.model.getAttr(grb.GRB.Attr.ObjVal), LPbound, solveTime]
            
            elif self.model.getAttr(grb.GRB.Attr.SolCount) > 0:
                fields = [self.model.modelname, self.name, self.G.n, self.G.m, self.G.d,
                          "NA", status, nonzerosCount, 
                          self.model.getAttr(grb.GRB.Attr.NodeCount),
                          self.model.getAttr(grb.GRB.Attr.ObjVal), LPbound, "TLR"]
            
            elif LPbound>self.G.n or LPbound <0.5:
                    fields = [self.model.modelname, self.name, self.G.n, self.G.m, self.G.d, "NA", status,
                           nonzerosCount, 
                          self.model.getAttr(grb.GRB.Attr.NodeCount),
                          "1", self.G.n, "TLR"]
            else:
                fields = [self.model.modelname, self.name, self.G.n, self.G.m, self.G.d,"NA", status,
                          nonzerosCount, 
                          self.model.getAttr(grb.GRB.Attr.NodeCount),
                          "1", LPbound, "TLR"]
            
            csvwriter.writerow(fields)
            
    
    def setModelAttr(self):
        self.model.setParam(grb.GRB.Param.NodefileStart, 10) #use at most 10GB per thread
        self.model.setParam(grb.GRB.Param.Cuts, 0)  #turn off cuts
        self.model.setParam(grb.GRB.Param.Presolve, 0)  #turn off presolve
        self.model.setParam(grb.GRB.Param.Heuristics, 0)  #turn off heuristics
        self.model.setParam(grb.GRB.Param.Method, 2)  #-1=automatic, 0=primal simplex, 1=dual simplex, 2=barrier, 3=concurrent, 4=deterministic concurrent, 5=deterministic concurrent simplex
        self.model.setParam(grb.GRB.Param.MIPGap, 0.0)  #force Gurobi to prove optimality (gap=0.0)
        self.model.setParam(grb.GRB.Param.TimeLimit, 3600) #set time limit
        
    def statusNumtoString(num):
        if num == 1: return "Model is loaded, but no solution information is available."
        elif num == 2: return "Model was solved to optimality (subject to tolerances), and an optimal solution is available."
        elif num == 3: return "Model was proven to be infeasible."
        elif num == 4: return "Model was proven to be either infeasible or unbounded. To obtain a more definitive conclusion, set the DualReductions parameter to 0 and reoptimize."
        elif num == 5: return "Model was proven to be unbounded. Important note: an unbounded status indicates the presence of an unbounded ray that allows the objective to improve without limit. It says nothing about whether the model has a feasible solution. If you require information on feasibility, you should set the objective to zero and reoptimize."
        elif num == 6: return "Optimal objective for model was proven to be worse than the value specified in the Cutoff parameter. No solution information is available."
        elif num == 7: return "Optimization terminated because the total number of simplex iterations performed exceeded the value specified in the IterationLimit parameter, or because the total number of barrier iterations exceeded the value specified in the BarIterLimit parameter."
        elif num == 8: return "Optimization terminated because the total number of branch-and-cut nodes explored exceeded the value specified in the NodeLimit parameter."
        elif num == 9: return "Optimization terminated because the time expended exceeded the value specified in the TimeLimit parameter."
        elif num == 10: return "Optimization terminated because the number of solutions found reached the value specified in the SolutionLimit parameter."
        elif num == 11: return "Optimization was terminated by the user."
        elif num == 12: return "Optimization was terminated due to unrecoverable numerical difficulties."
        elif num == 13: return "Unable to satisfy optimality tolerances; a sub-optimal solution is available."
        elif num == 14: return "An asynchronous optimization call was made, but the associated optimization run is not yet complete."
        elif num >= 15 or num <= 0: return "No specific error could be recognized."
    
   

class conflict(formulation):
    
    def __init__(self, graph):
        
        super().__init__(graph)
        
        if 3 * (comb(self.G.n, 2) - self.G.m) + self.G.n >= self.threshold:
            with open("resultsforclique.csv",'a',newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["c",self.name,self.G.n, self.G.m, self.G.d ,"NA", "Abort before build",
                                    "NA","NA","NA","NA","NA"])
                sys.exit(0)
        
        self.model.modelname="c"
        for i in range(self.G.n):
            self.x.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, obj = 1, name = "x_{%g}" % i))

        self.model.update()    

        self.model.setObjective(grb.quicksum(self.x[i] for i in range(self.G.n)))

        for i in range(self.G.n):
            k = 0
            j = i + 1
            while(k<self.G.degree[i] and j < self.G.n):               
                if(j < self.G.adjLists[i][k]):
                    self.model.addConstr(self.x[i] + self.x[j] <= 1)
                    j += 1
                else:
                    k += 1 
                    if(j == self.G.adjLists[i][k-1]):  
                        j += 1 
            while(j < self.G.n):
                self.model.addConstr(self.x[i] + self.x[j] <= 1)
                j += 1                
    
        self.model.update()
        
class sparse(formulation):
    
    def __init__(self, graph):
        
        super().__init__(graph)
        
        if 5*self.G.n + self.G.m >= self.threshold:
            with open("resultsforclique.csv",'a',newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["s", self.name, self.G.n, self.G.m, self.G.d ,"NA", "Abort before build",
                                    "NA","NA","NA","NA","NA"])
                sys.exit(0)

        self.model.modelname="s"
        self.z = self.model.addVar(vtype=grb.GRB.CONTINUOUS, name = "z")
        
        for i in range(self.G.n):
            self.x.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, obj = 1, name = "x_{%g}" % i))

        for i in range(self.G.n):
            self.y.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, name = "y_{%g}" % i))
        
        self.model.setObjective(self.z)

        self.model.update()

        self.model.addConstr(grb.quicksum(self.x[i] for i in range(self.G.n)) == self.z)

        for i in range(self.G.n):
            self.model.addConstr(self.z-grb.quicksum(self.x[j] for j in self.G.adjLists[i])-self.x[i] <= (self.G.n-(self.G.degree[i])-1) *(1-self.x[i]))    

        self.model.update()  

class conflictBalas(formulation):
    
    def __init__(self, graph):
        
        super().__init__(graph)
      
        #uncomment of you want to abort the code if the best estimation
            #the number of nonzeros passes the threshold
            
      #  if 3 * self.G.n*comb(self.G.d, 2) + 4*self.G.n + 2*self.G.m >= self.threshold:
       #     with open("resultsforclique.csv",'a',newline='') as csvfile:
        #        csvwriter = csv.writer(csvfile)
          #      csvwriter.writerow(["cB",self.name,self.G.n, self.G.m, self.G.d ,"NA", "Abort before build",
          #                         "NA","NA","NA","NA","NA"])
           #     sys.exit(0)
        
        self.model.modelname="cB"
            
                
        for i in range(self.G.n):
            self.x.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, name = "x_{%g}" % i))

        for i in range(self.G.n):
            self.y.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, name = "y_{%g}" % i))

        w = {}
        for i in range(self.G.n):
            for j in self.G.rightNeigh[i]: 
                w[i, j] = self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, name = "w_{%g,%g}" % (i, j))

        self.model.update()   

        self.model.setObjective(grb.quicksum(self.x[i] for i in range(self.G.n)))

        for i in range(self.G.n):
            for j in range(self.G.rightDegree[i]):
                for k in range(j+1, self.G.rightDegree[i]):
                    v_j = self.G.rightNeigh[i][j]
                    v_k = self.G.rightNeigh[i][k]
                    pos = bisect_left(self.G.adjLists[v_k],v_j)
                    if (pos == self.G.degree[v_k] or self.G.adjLists[v_k][pos] != v_j):              
                        self.model.addConstr(w[i, v_j] + w[i, v_k] <= self.y[i])

        for i in range(self.G.n):
            self.model.addConstr(grb.quicksum(w[j, i] for j in self.G.leftNeigh[i]) + self.y[i] == self.x[i])
        
        for i in range(self.G.n):
            for j in self.G.rightNeigh[i]:
                self.model.addConstr(w[i, j] <= self.y[i])

        self.model.addConstr(grb.quicksum(self.y[i] for i in range(self.G.n)) == 1)
        
        self.model.update()



class sparseJeroslow(formulation):

    def __init__(self, graph):

        super().__init__(graph)
        
        if 4*self.G.n + self.G.m >= self.threshold:
            with open("resultsforclique.csv",'a',newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["sJ",self.name,self.G.n, self.G.m, self.G.d ,"NA", "Abort before build",
                                    "NA","NA","NA","NA","NA"])
                sys.exit(0)
                
        self.model.modelname="sJ"       
        self.z = self.model.addVar(vtype=grb.GRB.CONTINUOUS, name = "z")

        for i in range(self.G.n):
            self.x.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, obj = 1, name = "x_{%g}" % i))

        for i in range(self.G.n):
            self.y.append(self.model.addVar(vtype = grb.GRB.CONTINUOUS, lb = 0, ub = 1, name = "y_{%g}" % i))
        
        self.model.setObjective(self.z)

        self.model.update()
        
        for i in range(self.G.n):
            self.y[i].BranchPriority=1

        self.model.addConstr(grb.quicksum(self.x[i] for i in range(self.G.n)) == self.z)

        for i in range(self.G.n):
            self.model.addConstr(self.z-grb.quicksum(self.x[j] for j in self.G.adjLists[i])-self.x[i] <= (self.G.n-(self.G.degree[i])-1) *(1-self.x[i]))  

        for i in range(self.G.n):
            self.model.addConstr(self.y[i] <= self.x[i])
            self.model.addConstr(self.y[i] + grb.quicksum(self.y[j] for j in self.G.leftNeigh[i]) >= self.x[i])
        
        self.model.addConstr(grb.quicksum(self.y[i] for i in range(self.G.n)) <= 1)
        
        self.model.update()

