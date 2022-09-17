import re
import time

from networkx import Graph
from pulp import LpVariable, LpProblem, LpMinimize, LpInteger, lpSum, LpStatus, LpStatusInfeasible, CPLEX_CMD

from aux import config
from aux.InfeasibleSolutionException import InfeasibleSolutionException


class KLabeling:

    def __init__(self, g: Graph, layers: int = 1):
        self.g = g
        self.layers = layers
        self.labeling = dict()
        self.start_time = None
        self.end_time = None
        self.log = ""

    def get_log(self) -> str:
        return self.log

    def label_alt(self):
        print("Number of nodes: {}".format(len(self.g.nodes)))
        print("Number of edges: {}".format(len(self.g.edges)))
        print("Layers: {}".format(self.layers))

        self.start_time = time.time()

        solver = CPLEX_CMD(path=config.cplex_path, msg=False, keepFiles=config.keep_files, timeLimit=config.time_limit)
        cmbs = [(i, i + 1) for i in range(self.layers)]
        cmbs.extend([(i + 1, i) for i in range(self.layers)])

        bounds = ["l", "u"]

        # Variables
        x_vars = LpVariable.dicts("x", (self.g.nodes, bounds), 1, self.layers + 1, cat=LpInteger)

        s_vars = LpVariable.dicts("s", (self.g.edges, cmbs), 0, 1, LpInteger)

        d_vars = LpVariable.dicts("d", self.g.nodes, cat=LpInteger)

        # The semiperimeter
        S = LpVariable("S", 0, cat=LpInteger)

        lpvc = LpProblem("VC", LpMinimize)

        if config.objective == "semi":
            lpvc += S
        else:
            lpvc += 1
        lpvc += lpSum(d_vars) == S

        M = 10000

        for e in self.g.edges:
            for l in [i for i in range(self.layers)]:
                lpvc += x_vars[e[0]]["l"] <= (l + 1) * (M * (1 - s_vars[e][(l, l + 1)]) + 1)
                lpvc += x_vars[e[0]]["u"] >= (l + 1) * s_vars[e][(l, l + 1)]
                lpvc += x_vars[e[1]]["l"] <= (l + 2) * (M * (1 - s_vars[e][(l, l + 1)]) + 1)
                lpvc += x_vars[e[1]]["u"] >= (l + 2) * s_vars[e][(l, l + 1)]

                lpvc += x_vars[e[0]]["l"] <= (l + 2) * (M * (1 - s_vars[e][(l + 1, l)]) + 1)
                lpvc += x_vars[e[0]]["u"] >= (l + 2) * s_vars[e][(l + 1, l)]
                lpvc += x_vars[e[1]]["l"] <= (l + 1) * (M * (1 - s_vars[e][(l + 1, l)]) + 1)
                lpvc += x_vars[e[1]]["u"] >= (l + 1) * s_vars[e][(l + 1, l)]
            lpvc += lpSum(s_vars[e]) == 1

        for v in self.g.nodes:
            lpvc += d_vars[v] == x_vars[v]["u"] - x_vars[v]["l"] + 1
            lpvc += x_vars[v]["u"] >= x_vars[v]["l"]

        # for l in range(self.layers + 1):
        #     if l % 2 == 0:
        #         lpvc += lpSum([x_vars[v][l] for v in self.g.nodes]) <= config.max_rows
        #     else:
        #         lpvc += lpSum([x_vars[v][l] for v in self.g.nodes]) <= config.max_columns

        # Required constraint: root node and leaf node must be given a label V
        if config.io_constraints:
            for (v, d) in self.g.nodes(data=True):
                if d["root"]:
                    if self.layers % 2 == 0:
                        lpvc += x_vars[v]["u"] == self.layers
                    else:
                        lpvc += x_vars[v]["u"] == self.layers - 1
                if d["terminal"]:
                    lpvc += x_vars[v]["l"] == 0

        lpvc.solve(solver)

        if lpvc.status == LpStatusInfeasible:
            raise InfeasibleSolutionException("Infeasible solution.")

        self.end_time = time.time()

        self.log += 'ILP time (s): {}\n'.format(self.end_time - self.start_time)

        # for v in self.g.nodes:
        #     for l in range(self.layers + 1):
        #         print("v_{}_{} = {}".format(v, l, x_vars[v][l].varValue))

        rows = 0
        columns = 0
        bucket = [0 for l in range(self.layers + 1)]
        for v in self.g.nodes:
            lower = int(round(x_vars[v]["l"].varValue))
            upper = int(round(x_vars[v]["u"].varValue))
            print("{}: {} {}".format(v, lower, upper))
            for i in range(lower, upper + 1):
                bucket[i - 1] += 1

        for l in range(self.layers + 1):
            s = bucket[l]
            print("Layer {}: {}".format(l, s))
            self.log += 'Layer {}: {}\n'.format(l, s)
            if l % 2 == 0 and s > rows:
                rows = s
            elif l % 2 == 1 and s > columns:
                columns = s
        self.log += 'Rows: {}\n'.format(rows)
        self.log += 'Columns: {}\n'.format(columns)

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
            lower = int(round(x_vars[v]["l"].varValue))
            upper = int(round(x_vars[v]["u"].varValue))
            for i in range(lower, upper + 1):
                node_assignments[v].append(i - 1)

        self.labeling = (rows, columns, node_assignments, edge_assignments)

        # if config.verbose:
        print("Status:", LpStatus[lpvc.status])
        print("Sum = " + str(S.varValue))
        # print('Node assignments: {}\n'.format(node_assignments))
        # print('Edge assignments: {}\n'.format(edge_assignments))

        config.log.add(self.get_log())

        return self.labeling

    def label(self):
        print("Number of nodes: {}".format(len(self.g.nodes)))
        print("Number of edges: {}".format(len(self.g.edges)))
        print("Layers: {}".format(self.layers))

        self.start_time = time.time()

        solver = CPLEX_CMD(path=config.cplex_path, msg=False, keepFiles=config.keep_files, timeLimit=config.time_limit,
                           logPath=str(config.root.joinpath("cplex.log")))

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
                    if config.output_layer is not None:
                        lpvc += x_vars[v][config.output_layer] == 1
                    else:
                        if self.layers % 2 == 0:
                            lpvc += x_vars[v][self.layers] == 1
                        else:
                            lpvc += x_vars[v][self.layers - 1] == 1
                elif d["terminal"]:
                    if config.input_layer is not None:
                        lpvc += x_vars[v][config.input_layer] == 1
                    else:
                        lpvc += x_vars[v][0] == 1

        # lpvc.writeLP('ilp.lp')
        lpvc.solve(solver)

        if lpvc.status == LpStatusInfeasible:
            raise InfeasibleSolutionException("Infeasible solution.")

        self.end_time = time.time()

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
        self.log += 'Rows: {}\n'.format(rows)
        self.log += 'Columns: {}\n'.format(columns)
        self.log += 'Objective: {}\n'.format(S.varValue)

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
