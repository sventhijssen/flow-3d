from aux.UndecidedException import UndecidedException
from cli.Program import Program

benchmarks = [
    ('5xp1.pla', True),
    ('apex2.pla', True),
    ('clip.pla', True),
    ('cm163a.pla', True),
    ('cmb.pla', True),
    ('cordic.pla', True),
    ('cps.pla', True),
    ('frg1.pla', True),
    ('ham15.pla', True),
    ('in0.pla', True),
    ('misex1.pla', True),
    ('misex3.pla', True),
    ('pdc.pla', True),
    ('spla.pla', True),
    ('tial.pla', True)
]

layers = [2, 4]  # Here, the number of layers denotes the number of memristor layers
time_limit = 10800  # seconds

for layer in layers:
    for (benchmark, sbdd) in benchmarks:
        if sbdd:
            bdd = "sbdd"
        else:
            bdd = "robdd"

        # The number of layers can be set using the flag -l LAYERS
        log_file_name = benchmark + '_' + bdd + '_' + str(layer) + '_optimal.log'
        raw_command = 'new_log {} | read benchmarks/{} | {} -m | compact -l {} -t {} -keep'.format(log_file_name, benchmark, bdd, layer, time_limit)

        try:
            Program.execute(raw_command)
        except UndecidedException as e:
            print("Exceeded maximum time.")
