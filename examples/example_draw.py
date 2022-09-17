from aux.UndecidedException import UndecidedException
from cli.Program import Program

benchmark_name = "5xp1"
benchmark_filename = benchmark_name + ".pla"
sbdd = True
layer = 2  # Here, the number of layers denotes the number of memristor layers
time_limit = 10800  # seconds

if sbdd:
    bdd = "sbdd"
else:
    bdd = "robdd"

log_file_name = benchmark_name + '_' + bdd + '_' + str(layer) + '_test.log'
matrix_name = "dot_" + benchmark_name
raw_command = 'new_log {} | read benchmarks/{} | {} -m | compact -l {} -t {} -keep | draw_matrix {}'.format(log_file_name, benchmark_filename, bdd, layer, time_limit, matrix_name)

try:
    Program.execute(raw_command)
except UndecidedException as e:
    print("Exceeded maximum time.")
