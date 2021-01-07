
class Graph:
    
    def __init__(self, *args, **kwargs):
   
        try:
            self.n = 0
            self.m = 0
            self.adjLists = []
            self.degree = 0
            self.Delta = 0
            self.d = 0
            self.rightDegree = [] 
            self.ordering = []
            self.position = []
            self.leftNeigh = []
            self.rightNeigh = []
            f = open(kwargs.get('inputfile'), 'r')
            line = f.readline()
            fields = str.split(line)
            self.n = int(fields[0])
            self.m = int(fields[1])
    
            for i in range(0, self.n):
                self.adjLists.append([])
    
            self.degree = [0]*self.n
    
            for line in f:
                fields = line.split(' ')
                i = int(fields[0])
                j = int(fields[1])
                self.adjLists[i].append(j)
                self.adjLists[j].append(i)
                self.degree[i] += 1
                self.degree[j] += 1
    
            f.close
    
            for i in range(0, self.n):
                self.adjLists[i].sort()
                if (self.degree[i]>self.Delta):
                    self.Delta = self.degree[i]
    
            inputfile = kwargs.get('inputfile').split('/')
            self.name = inputfile[len(inputfile)-1]
        except:
            self.n=kwargs.get('numNodes')
            self.m = 0
            self.adjLists = []
            self.degree = 0
            for i in range(0, self.n):
                self.adjLists.append([])
                
            self.degree = [0]*self.n
       

    
    
    def __str__(self):
        text = 'n = ' + str(self.n) + '\nm = ' + str(self.m) + '\nDelta = ' + str(self.Delta)
        for i in range(self.n):
            text += ('\n' + str(i) + '(' + str(self.degree[i]) + ')' + str(self.adjLists[i]))
        return text    

    def degOrdering(self):

        self.rightDegree = [0]*self.n
        self.ordering = [0]*self.n
        self.position = [0]*self.n

        buckets = [0]*(self.Delta + 1)

        for i in range(self.n):
            self.rightDegree[i] = self.degree[i]
            buckets[self.rightDegree[i]] += 1
            self.leftNeigh.append([])
            self.rightNeigh.append([])

        count = 0

        for k in range(self.Delta + 1):
            temp = buckets[k]
            buckets[k] = count
            count += temp
 

        for i in range(self.n):
            self.position[i] = buckets[self.rightDegree[i]]
            self.ordering[self.position[i]] = i
            buckets[self.rightDegree[i]] += 1
    

        for k in range(self.Delta,0,-1):
            buckets[k] = buckets[k - 1]
    
        buckets[0] = 0

        for i in range(self.n):
        
            minV = self.ordering[i]

            buckets[self.rightDegree[minV]] += 1

            if (self.rightDegree[minV] > self.d):
                self.d = self.rightDegree[minV]
        
            for j in self.adjLists[minV]:
            
                neighbor = j

                if (self.position[neighbor] > self.position[minV]):
                    self.leftNeigh[neighbor].append(minV)
                    self.rightNeigh[minV].append(neighbor)
                
                    if (self.rightDegree[neighbor] == self.rightDegree[minV]):

                        if (neighbor != self.ordering[buckets[self.rightDegree[minV]]]):

                            pu = buckets[self.rightDegree[minV]]
                            u = self.ordering[pu]
                            self.ordering[pu] = neighbor
                            self.ordering[self.position[neighbor]] = u
                            self.position[u] = self.position[neighbor]
                            self.position[neighbor] = pu
                        
                        buckets[self.rightDegree[minV] - 1] = self.position[minV] + 1
                        buckets[self.rightDegree[neighbor]] += 1 
                        self.rightDegree[neighbor] -=1 
                    
                    else:

                        pu = buckets[self.rightDegree[neighbor]]
                        u = self.ordering[pu]

                        if (neighbor != u):

                            self.ordering[pu] = neighbor
                            self.ordering[self.position[neighbor]] = u
                            self.position[u] = self.position[neighbor]
                            self.position[neighbor] = pu
                        
                        buckets[self.rightDegree[neighbor]] += 1
                        self.rightDegree[neighbor] -=1
    
        for i in range(self.n):
            self.leftNeigh[i].sort()
            self.rightNeigh[i].sort()
        
    #this function is basically wrote by "https://www.geeksforgeeks.org/bipartite-graph/"        
    def isBipartite(self): 

        # Create a color array to store colors  
        # assigned to all veritces. Vertex 
        # number is used as index in this array.  
        # The value '-1' of  colorArr[i] is used to  
        # indicate that no color is assigned to  
        # vertex 'i'. The value 1 is used to indicate  
        # first color is assigned and value 0 
        # indicates second color is assigned. 
        
        #check if the graph is not empty set
        if self.n==0:
            return True 
        
        colorArr = [-1] * self.n 
  
        # Assign first color to vertex indexed with zero 
        colorArr[0] = 1
  
        # Create a queue (FIFO) of vertex numbers and  
        # enqueue source vertex for BFS traversal 
        queue = [] 
        queue.append(0) 
  
        # Run while there are vertices in queue  
        # (Similar to BFS) 
        while queue: 
            u = queue.pop() 
            for v in self.adjLists[u]: 
                 
                #if the neighbor v is not colored 
                if colorArr[v] == -1:   
                    # Assign alternate color to this  
                    # adjacent v of u 
                    colorArr[v] = 1 - colorArr[u] 
                    queue.append(v) 
  
                #if neighbor v is colored with same color as u 
                elif colorArr[v] == colorArr[u]: 
                    return False
  
        # If we reach here, then all adjacent  
        # vertices can be colored with alternate  
        # color 
        return True
    
    def createInducedGraph(self,S):
        #Finds the subgraph induced by all the nodes in S. S is sorted
        S_size = len(S)
        g=Graph(numNodes= S_size)
        reverseMap=[-1]*self.n
        
        for i in range(S_size):
            reverseMap[S[i]] = i

        for i in range(S_size):
            g.adjLists[i] = self.commonNeighborsList(S[i], S)
            g.degree[i] = len(g.adjLists[i])
            
            for j in range(g.degree[i]): #relabel the vertices for the new, smaller graph
                g.adjLists[i][j] = reverseMap[g.adjLists[i][j]]
            g.m += g.degree[i]

        g.m /= 2
        return g
    def commonNeighborsList(self, u, v):
        t=[]
        q = 0
        q1 = 0
        qend = self.degree[u]
        q1end = len(v)
        ptr = self.adjLists[u] if qend != 0 else None
        ptr1 = v if q1end != 0 else None
        
        
        while (q1<q1end and q<qend):
            t1 = ptr[q]
            t2=ptr1[q1]
		    
            if (t1 == t2):
                t.append(t1)
                q+=1
                q1+=1   
            elif (t1>t2):
                q1+=1    
            else:
                q+=1
        return t
    #turns the graph into its complement:
    def complementGraph(self):
        self.m = self.n*(self.n - 1) / 2 - self.m
        for i in range(self.n):
            self.degree[i] = self.n - self.degree[i] - 1 #update degrees
            self.adjLists[i]=list(set([j for j in range(self.n) if j!=i])\
                         -set(self.adjLists[i]))
            self.adjLists[i].sort()
            
    def isconflictBalasPerfect(self):
        self.degOrdering()
        for i in range(self.n):
            g=self.createInducedGraph(self.rightNeigh[i])
            g.complementGraph()
            if g.isBipartite()==False:
                return False
        return True   
