## Command line

Using command line, one can run the program using the following template:

If no BDD is available:
```bash
python3 cli/main.py new_log LOG_NAME | read BENCHMARK_NAME | BDD_TYPE -m | compact -l {} -t {} -keep 
```

#### Log file
It is best to record your experiments with a log. To set up a new log, use ```new_log LOG_FILENAME```. It is best practice to use the file extension ``.log``. Note that a log file will be overridden when the same log name is used.

#### Benchmark
Benchmarks are located in the folder [_benchmarks_](/benchmarks).
Depending on the OS, locate the relative file path as follows (make sure to use the correct file separator `\ ` or `/ `):

```
benchmarks/tial.pla
```

#### BDD type
Two BDD types can be used: ```robdd``` and ```sbdd```.

#### BDD file
One can write a BDD to file using the command ```write_bdd BDD_FILENAME```. It is best practice to use the file extension ``.bdd``.

#### COMPACT
COMPACT can be called using optional arguments. These include:
##### Gamma
When COMPACT for 2D crossbars is used, a user-defined parameter gamma can be set. Gamma has a value between [0,1]. When gamma = 0, a solution with minimal semiperimeter is sought. When gamma = 1, a solution with minimal maximum dimension is sought (i.e. a more square solution).
A verbose output is printed to the screen.
```bash
-gamma VALUE
```

##### Layers
When mapping to 3D crossbars, the number of layers can be defined. Here, the parameter denotes the number of memristor layers. Note that the number of nanowire layers is the number of memristor layers plus one.
```bash
-l VALUE
``` 

##### Labeling method
One can use the traditional VH-labeling method as proposed in the TCAD journal using the following flag:

```bash
-vh
```

##### I/O constraints
One can turn off the I/O constraints by passing the following flag:

```bash
-io
```

#### Area constraints
One can define constraints on the area using the following parameters:
```bash
-r VALUE -c VALUE
```
Usually VALUE is a power of two (128, 256, 512, 1024, ....)

#### Timeout
One can define a timeout on the ILP formulation. The duration for the timeout is defined in seconds.
```bash
-t DURATION
```

## Examples
Below, a small set of examples is provided:

```bash
python3 cli/main.py new_log tial.log | read benchmarks/t481.pla | robdd -m | compact -l 3 -t 60 -keep
```

```bash
python3 cli/main.py new_log tial.log | read benchmarks/t481.pla | sbdd -m | compact -vh -t 900
```