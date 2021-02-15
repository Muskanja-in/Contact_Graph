import numpy as np
import pandas as pd


def Update_result(result, Merge):
    
    Updated_result = np.copy(result)
    
    for k in range(len(Merge)):
        x = Merge[k][0]
        y = Merge[k][1]
        Updated_result[x] = np.add(Updated_result[x], Updated_result[y])
        Updated_result[y] = np.zeros(len(result), int)
    
    return Updated_result 



def Update_W_result(W_result, W_sum, result, Merge):
    
    Updated_W_result = np.copy(W_result)
    
    for k in range(len(Merge)):
        x = Merge[k][0]
        y = Merge[k][1]
        W_sum[x] = np.add(W_sum[x], W_sum[y])
        W_sum[y] = 0
        
    TotalNodes = np.sum(result, axis  = 1)
    
    t1 = 0
    for l in Updated_W_result:
        
        if TotalNodes[t1]>0:
            Updated_W_result[t1] = W_sum[t1]/TotalNodes[t1]
        else:
            Updated_W_result[t1] = 0
        t1 = t1 + 1

    return Updated_W_result



def Update_S_result(S_result, S_sum, result, Merge):
    
    Updated_S_result = np.copy(S_result)

    for k in range(len(Merge)):
        x = Merge[k][0]
        y = Merge[k][1]
        
        for l in range(len(result)):   
            S_sum[x][l] = np.add(S_sum[x][l], S_sum[y][l])
            S_sum[y][l] = 0
            
        for l in range(len(result)):   
            S_sum[l][y] = 0
            
        for l in range(len(result)):   
            Updated_S_result[y][l] = 0
            Updated_S_result[l][y] = 0
        
        S_sum[x][x] = 0
    
    TotalNodes = np.sum(result, axis  = 1)
    t1 = 0
    for row in Updated_S_result:
        t2 = 0
        for value in row:
            if TotalNodes[t1]>0 and TotalNodes[t2]>0:
                Updated_S_result[t1][t2] = S_sum[t1][t2]/(TotalNodes[t1]*TotalNodes[t2])
                
            t2 = t2 + 1
        t1 = t1 + 1
    t2 = 0
    t1 = 0
    
    return Updated_S_result



def Update_edges(result, Merge, Number_of_edges):
    
    for k in range(len(Merge)):
        x = Merge[k][0]
        y = Merge[k][1]
        
        for l in range(len(result)):
           
            Number_of_edges[x][l] = np.add(Number_of_edges[x][l], Number_of_edges[y][l])
            Number_of_edges[y][l] = 0
            
        for l in range(len(result)):
            Number_of_edges[l][y] = 0
        
        Number_of_edges[x][x] = 0
    
    return Number_of_edges        



def UpdateInter(Inter, result, Number_of_edges):
    
    TotalNodes = np.sum(result, axis  = 1)
    
    p = 0
    for row in Inter:
        q = 0
        for value in row:
            if Number_of_edges[p][q]>= TotalNodes[p] and Number_of_edges[p][q]>= TotalNodes[q] and not Number_of_edges[p][q]==0: 
                Inter[p][q] = 1
            else:
                Inter[p][q] = 0
            q = q + 1
        p = p + 1
    
    return Inter



def Detect_Cluster(W ,S):
    
    #Result will provide a matrix with same size as S, indicating number of cluster 
    
    n = len(S)
    
    result = np.identity(n, int)
    W_result = np.copy(W)
    S_result = np.copy(S)
    W_sum = np.copy(W)
    S_sum = np.copy(S)
    
    Available = np.ones(n, int) # 1-Available, 0-Not available
    Inter = np.zeros((n, n), int)
    Number_of_edges = np.zeros((n, n), int)
    Merge = []
    Stop = False
    
    #Initializing Number_of_edges and Inter(Inter Interested cluster matrix)
    #Variables t1, t2, t3, t4 are used just for supporting loops
    
    t1 = 0
    for row in Number_of_edges:
        t2 = 0
        for value in row:
            if S_result[t1][t2]>0 and not t1==t2:
                Number_of_edges[t1][t2] = 1
                Inter[t1][t2] = 1
            t2 = t2 + 1
        t1 = t1 + 1
    
    #While loop is to repeatedly merge the clusters into communities
    
    t1 = 0
    while(Stop == False):
        
        t2 = 0
        for row in S_result:
                        
            x = t2
            max_value = np.amax(row)
            t3 = 0
            for k in row:
                if k == max_value and not t3 == t2:
                    y = t3
                    break
                t3 = t3 + 1
            t3 = 0
              
            
            if Available[x] == 1 and Available[y] == 1 and Inter[x][y] == 1:
                if S_result[x][y] > np.add(W_result[x], W_result[y]):
                    
                    Merge = Merge + [[x, y]]
                    Available[x] = 0
                    Available[y] = 0
                    
            t2 = t2 + 1   
        t2 = 0
    
    #Updating result and other matrix through already defined functions
        
        Previous_result = result
        result = Update_result(result, Merge)
        W_result = Update_W_result(W_result, W_sum, result, Merge)
        S_result = Update_S_result(S_result, S_sum, result, Merge)
        
        Number_of_edges = Update_edges(result, Merge, Number_of_edges)
        Inter = UpdateInter(Inter, result, Number_of_edges)
        Available = np.ones(n, int)
        Merge = []
        
    #Checking whether the clustering has come to an end to finish the looping
        
        Structure_same = False
        if t1>10:
            comparision = Previous_result == result
            Structure_same = comparision.all()
        
        One_cluster_left = False
        t2 = 0
        for row in result:
            if np.amax(row)==0:
                t2 = t2 + 1
        if t2 == len(result)-1:
            One_cluster_left = True
        t2 = 0
             
        if Structure_same or One_cluster_left:
            Stop = True
        
        t1 = t1 + 1
    
    #While loop ends here    
    
    
    Modified_result = np.copy(result)
    t2 = 0
    for row in Modified_result:
        if np.amax(row) == 0:
            Modified_result = np.delete(Modified_result, t2, axis=0)    
        else:
            t2 = t2 + 1
    t2 = 0
    
    Modified_result = Modified_result.transpose()

    output ={
    }
    
    t2=0
    for row in Modified_result:
        t3=0
        for value in row:
            if Modified_result[t2][t3]==1:
                output[t2+1] = t3 + 1
            t3 += 1
        t2 += 1
            
    print(output)
    



