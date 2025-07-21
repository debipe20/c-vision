"""
1192. Critical Connections in a Network
There are n servers numbered from 0 to n - 1 connected by undirected server-to-server connections forming a network where connections[i] = [ai, bi] represents a connection between servers ai and bi. Any server can reach other servers directly or indirectly through the network.

A critical connection is a connection that, if removed, will make some servers unable to reach some other server.

Return all critical connections in the network in any order.

Input: n = 4, connections = [[0,1],[1,2],[2,0],[1,3]]
Output: [[1,3]]
Explanation: [[3,1]] is also accepted

"""
from collections import defaultdict

def criticalConnections(n, connections):
    

    graph = defaultdict(list) # use a defaultdict to store the graph as an adjacency list.
    for u, v in connections:
        graph[u].append(v) #Since the graph is undirected,  add the edge in both directions: u → v and v → u
        graph[v].append(u)

    discovery = [-1] * n #time when node i is first visited in DFS.
    low = [-1] * n #the lowest discovery time reachable from i via DFS or a back edge.
    time = [0] #a mutable counter (wrapped in a list so it can be updated inside recursion).
    result = [] #stores the critical connections (bridges).

    def dfs(u, parent):
        discovery[u] = low[u] = time[0]
        time[0] += 1

        for v in graph[u]:
            if v == parent:
                continue
            if discovery[v] == -1: #If neighbor v is not yet visited, do a DFS on it.
                dfs(v, u)
                low[u] = min(low[u], low[v]) #After recursion, update low[u] based on the lowest reachable from v.

                if low[v] > discovery[u]: #If no back edge from v or its subtree to u or above, then edge (u, v) is a bridge.
                    result.append([u, v])
            else:
                low[u] = min(low[u], discovery[v]) #If v is already visited, it’s a back edge.Update low[u] to the lowest discovery time seen.

    dfs(0, -1)
    return result


n = 4
connections = [[0,1],[1,2],[2,0],[1,3]]
print(criticalConnections(n, connections))