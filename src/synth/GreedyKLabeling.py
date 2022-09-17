import re
import time

from networkx import Graph, bfs_successors
from pulp import LpVariable, LpProblem, LpMinimize, LpInteger, lpSum, LpStatus, LpStatusInfeasible, CPLEX_CMD

from aux import config
from aux.InfeasibleSolutionException import InfeasibleSolutionException


class GreedyKLabeling:

    def __init__(self, g: Graph, layers: int = 1):
        self.g = g
        self.layers = layers
        self.labeling = dict()
        self.breadth_first_search_start_time = None
        self.breadth_first_search_end_time = None
        self.ilp_start_time = None
        self.ilp_end_time = None
        self.log = ''

    def get_log(self) -> str:
        content = ''
        content += 'Breadth-first search time (s): {}\n'.format(
            self.breadth_first_search_end_time - self.breadth_first_search_start_time)
        content += 'ILP time (s): {}\n'.format(
            self.ilp_end_time - self.ilp_start_time)
        return self.log + content

    def label(self):
        print("Number of nodes: {}".format(len(self.g.nodes)))
        print("Number of edges: {}".format(len(self.g.edges)))
        print("Layers: {}".format(self.layers))

        self.breadth_first_search_start_time = time.time()

        node_assignments = dict()
        count_up = dict()

        start_node = None

        if config.io_constraints:
            for (v, d) in self.g.nodes(data=True):
                if d["root"]:
                    if self.layers % 2 == 0:
                        node_assignments[v] = self.layers
                        count_up[v] = False
                    else:
                        node_assignments[v] = self.layers - 1
                        count_up[v] = False
                if d["terminal"]:
                    if start_node is None:
                        start_node = v
                    node_assignments[v] = 0
                    count_up[v] = True
        else:
            for (v, d) in self.g.nodes(data=True):
                if d["terminal"]:
                    if start_node is None:
                        start_node = v
                    node_assignments[v] = 0
                    count_up[v] = True

        conflicts = set()
        dummy_nodes = set()
        for (v, successors) in bfs_successors(self.g, start_node):
            for successor in successors:
                # If the successor is not yet given a label, so we give it a label l+1 or l-1 (within bounds).
                # Otherwise, the successor is already given a label and we resolve any potential conflicts.
                if successor not in node_assignments:

                    # If we are counting up and we have reached the maximum number of layers,
                    # we must count up from this point.
                    # Otherwise, we continue counting up/down as the current node v.
                    if count_up[v] and node_assignments[v] == self.layers:
                        count_up[v] = False
                        count_up[successor] = False
                    else:
                        count_up[successor] = count_up.get(v)

                    # If we are counting down and we have reached the minimum number of layers,
                    # we must count up from this point.
                    # Otherwise, we continue counting up/down as the current node v.
                    if not count_up[v] and node_assignments[v] == 0:
                        count_up[v] = True
                        count_up[successor] = True
                    else:
                        count_up[successor] = count_up.get(v)

                    # If we are counting up, then we increment the label for his successor.
                    # Otherwise, we decrement the label for this successor.
                    if count_up[v]:
                        node_assignments[successor] = node_assignments[v] + 1
                    else:
                        node_assignments[successor] = node_assignments[v] - 1

                else:
                    # If both the current node and its success have the same label, we mark the conflict.
                    # Otherwise, if the absolute distance between both nodes is greater than 1,
                    # we must insert intermediate nodes.
                    # Else, the labeling is fine.
                    if node_assignments[successor] == node_assignments[v]:
                        conflicts.add((v, successor))
                    elif abs(node_assignments[successor] - node_assignments[v]) > 1:
                        dummy_nodes.add((v, successor))
                    else:
                        pass

        self.breadth_first_search_end_time = time.time()

        print("Greedy labeling done.")

        self.ilp_start_time = time.time()

        solver = CPLEX_CMD(path=config.cplex_path, msg=False, timeLimit=config.time_limit)
        cmbs = [(i, i + 1) for i in range(self.layers)]
        cmbs.extend([(i + 1, i) for i in range(self.layers)])

        # Variables
        x_vars = LpVariable.dicts("x", (self.g.nodes, [i for i in range(self.layers + 1)]), 0, 1, LpInteger)

        s_vars = LpVariable.dicts("s", (self.g.edges, cmbs), 0, 1, LpInteger)

        d_vars = LpVariable.dicts("d", self.g.nodes, cat=LpInteger)

        r = LpVariable("r", cat=LpInteger)
        c = LpVariable("c", cat=LpInteger)

        # The semiperimeter
        S = LpVariable("S", 0, cat=LpInteger)

        lpvc = LpProblem("VC", LpMinimize)

        if config.objective == "semi":
            lpvc += S
        else:
            lpvc += 1
        lpvc += S == r + c

        for e in self.g.edges:
            for l in [i for i in range(self.layers)]:
                lpvc += lpSum(x_vars[e[0]][l] + x_vars[e[1]][l+1]) >= 2 * s_vars[e][(l, l + 1)]
                lpvc += lpSum(x_vars[e[0]][l+1] + x_vars[e[1]][l]) >= 2 * s_vars[e][(l + 1, l)]
            lpvc += lpSum(s_vars[e]) == 1

        for v in self.g.nodes:
            lpvc += lpSum(x_vars[v]) == d_vars[v]

            for l1 in range(self.layers):
                for l2 in range(l1 + 1, self.layers + 1):
                    lpvc += 10000*(1-(x_vars[v][l1] + x_vars[v][l2] - 1)) + d_vars[v] >= l2 - l1 + 1

        for l in range(self.layers + 1):
            if l % 2 == 0:
                lpvc += lpSum([x_vars[v][l] for v in self.g.nodes]) <= r
                lpvc += lpSum([x_vars[v][l] for v in self.g.nodes]) <= config.max_rows
            else:
                lpvc += lpSum([x_vars[v][l] for v in self.g.nodes]) <= c
                lpvc += lpSum([x_vars[v][l] for v in self.g.nodes]) <= config.max_columns

        # Required constraint: root node and leaf node must be given a label V
        if config.io_constraints:
            for (v, d) in self.g.nodes(data=True):
                if d["root"]:
                    if self.layers % 2 == 0:
                        lpvc += x_vars[v][self.layers] == 1
                    else:
                        lpvc += x_vars[v][self.layers - 1] == 1
                elif d["terminal"]:
                    lpvc += x_vars[v][0] == 1

        # For each node in node_assignments, we set the x_vars value.
        for (v, l) in node_assignments.items():
            lpvc += x_vars[v][l] == 1

        # We add the dummy nodes to the graph.
        for (u, v) in dummy_nodes:
            min_layer = min(node_assignments[u], node_assignments[v])
            max_layer = max(node_assignments[u], node_assignments[v])

            # For each intermediate value in the interval (min_layer, max_layer), we introduce a dummy node.
            for i in range(min_layer + 1, max_layer):
                lpvc += x_vars[u][i] == 1

        # For the remaining conflicting nodes at layer l, we usually have two options:
        # we introduce a dummy node in layer l+1, or we introduce a dummy node in layer l-1.
        # Since we have freedom, we formulate this problem as an optimization problem where we solve the K-labeling.
        for (u, v) in conflicts:
            # If we have a conflict at layer 0, we can only use layer 1 to resolve.
            # Otherwise, if we have a conflict at layer self.layers, we can only use layer self.layers-1 to resolve.
            # Else, we can use either layer l-1 or l+1.
            if node_assignments[u] == 0:
                lpvc += x_vars[u][node_assignments[u] + 1] == 1
                # lpvc += x_vars[u][node_assignments[v] - 1] == 0
                # x_vars[u][node_assignments[v] - 1] == 1
            elif node_assignments[u] == self.layers:
                lpvc += x_vars[u][node_assignments[u] - 1] == 1
            else:
                lpvc += x_vars[u][node_assignments[u] + 1] + x_vars[u][node_assignments[v] - 1] == 1

        lpvc.writeLP('ilp.lp')
        lpvc.solve(solver)

        if lpvc.status == LpStatusInfeasible:
            raise InfeasibleSolutionException("Infeasible solution.")

        self.ilp_end_time = time.time()

        print("Status: ", LpStatus[lpvc.status])
        print("Objective: " + str(S.varValue))
        rows = 0
        columns = 0
        for l in range(self.layers + 1):
            s = sum([int(round(x_vars[v][l].varValue)) for v in self.g.nodes])
            print("Layer {}: {}".format(l, s))
            self.log += 'Layer {}: {}\n'.format(l, s)
            if l % 2 == 0 and s > rows:
                rows = s
            elif l % 2 == 1 and s > columns:
                columns = s

        edge_assignments = dict()
        for e in self.g.edges:
            for l in range(self.layers):
                if int(round(s_vars[e][(l, l + 1)].varValue)) == 1:
                    edge_assignments[e] = (l, l + 1)
                if int(round(s_vars[e][(l + 1, l)].varValue)) == 1:
                    edge_assignments[e] = (l + 1, l)

        node_assignments = dict()
        for v in self.g.nodes:
            node_assignments[v] = []

        for v in self.g.nodes:
            for l in range(self.layers + 1):
                if int(round(x_vars[v][l].varValue)) == 1:
                    node_assignments[v].append(l)

        self.log += 'Rows: {}\n'.format(rows)
        self.log += 'Columns: {}\n'.format(columns)
        self.log += 'Objective: {}\n'.format(S.varValue)

        self.labeling = (rows, columns, node_assignments, edge_assignments)

        config.log.add(self.get_log())

        gap = 0
        cplex_log_file_name = config.root.joinpath("cplex.log")
        if cplex_log_file_name.is_file():
            with open(str(cplex_log_file_name), 'r') as f:
                for line in f.readlines():
                    if "gap" in line:
                        gap = float(re.findall(r'(\d+\.\d+)\%', line)[0])
        config.log.add("Gap (%): {}\n".format(gap))

        return self.labeling
