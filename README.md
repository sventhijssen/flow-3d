# FLOW-3D: Flow-Based Computing on 3D Nanoscale Crossbars with Minimal Semiperimeter

## Note
FLOW-3D is  part of the [MemX](https://github.com/sventhijssen/memx) digital in-memory computing package. MemX supports both flow-based in-memory computing and path-based in-memory computing.

## Introduction
##### Flow-based computing
Flow-based computing is an in-memory computing paradigm on nanoscale memristor crossbars.
The memristors are assigned Boolean literals (Boolean variables and their negations), and the Boolean truth values '0' and '1'.

Definition:
Given a crossbar design for a Boolean function φ, then the Boolean function φ evaluates to true if and only if there exists a path along low resistive memristors from the input nanowire (bottom most nanowire) to the output nanowire (top most nanowire) when a high input voltage is applied to the input nanowire.

<img src="extra/demo.gif" alt="Flow-based computing" style="width:80%"/>

##### 3D nanoscale crossbars
In Figure (a) below, an example of a 2D crossbar is given; in Figure (b), an example of a 3D crossbar is given.
The 3D crossbar can be represented using a matrix representation, as shown in Figure (c), or a graph representation as in Figure (d).
Image from the FLOW-3D paper.
<img src="extra/2d_3d.png" alt="2D and 3D nanoscale crossbar" style="width:80%"/>

##### Publications
- Thijssen, S., Jha, S. K., & Ewetz, R. (2023). FLOW-3D: Flow-Based Computing on 3D Nanoscale Crossbars with Minimal Semiperimeter. In Asia and South Pacific Design Automation Conference (ASP-DAC). (accepted)

##### Related work
- Thijssen, S., Jha, S. K., & Ewetz, R. (2022). Equivalence Checking for Flow-Based Computing. International Conference on Computer Design (ICCD). (accepted)
- Thijssen, S., Jha, S. K., & Ewetz, R. (2022). [COMPACT: Flow-Based Computing on Nanoscale Crossbars with Minimal Semiperimeter and Maximum Dimension](https://ieeexplore.ieee.org/abstract/document/9662445). In IEEE Trans. on Computer-aided Design of Integrated Circuits and Systems (TCAD). (accepted)
- Thijssen, S., Jha, S. K., & Ewetz, R. (2021). [COMPACT: Flow-Based Computing on Nanoscale Crossbars with Minimal Semiperimeter](https://ieeexplore.ieee.org/abstract/document/9473995). In 2021 Design, Automation & Test in Europe Conference & Exhibition (DATE) (pp. 232-237). IEEE. **Nominated for Best Paper Award.**
- Thijssen, S., Jha, S. K., & Ewetz, R. (2022). [PATH: Evaluation of Boolean Logic using Path-based In-Memory Computing](https://sumitkumarjha.com/papers/2022_Jha_DAC_Path_Flow.pdf). In Design Automation Conference (DAC). (accepted)

## Requirements

##### Windows

- Install and enable [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10#install-windows-subsystem-for-linux). 
- Python 3.6 or higher
- Optional: CPLEX 20.1.0.0

##### Linux
- Python 3.6 or higher
- Optional: CPLEX 20.1.0.0

##### MacOS
- Python 3.6 or higher
- Optional: CPLEX 20.1.0.0

## Installation

##### Submodules
Clone this git repository and the required submodule ABC. For ABC, make sure to clone the submodule from [here](https://github.com/sventhijssen/abc).
Clone the submodules using the following command:

```bash
git submodule update --init --recursive
```

##### ABC
Compile the ``ABC`` tool in the directory _abc_. 

```bash
cd abc
make
```

##### CPLEX
By default, CPLEX is the ILP solver. 
Download and install [CPLEX](https://www.ibm.com/analytics/cplex-optimizer), 
and make sure CPLEX is installed and the variable `cplex_path` is set correctly for your OS.

##### Python packages and dependencies
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the Python dependencies in ``requirements.txt``.

```bash
pip3 install -r requirements.txt
```

##### LuaLaTeX
Install ``lualatex``.

## Usage

In the directory [_examples_](/examples), some examples are given on how to use FLOW-3D from command line.

```bash
python3 cli/main.py new_log tial.log | read benchmarks/tial.pla | robdd -m | compact -l 4
```

## Version
FLOW-3D version 1.0.0.  

## Contact
_Sven Thijssen  
University of Central Florida  
sven.thijssen (at) knights.ucf.edu  
http://sventhijssen.com/_

## References
- [ABC](https://people.eecs.berkeley.edu/~alanmi/abc/)
- [RevLib](http://www.informatik.uni-bremen.de/rev_lib/)
- [CPLEX](https://www.ibm.com/analytics/cplex-optimizer)
- [Computation of boolean formulas using sneak paths in crossbar computing](https://patentimages.storage.googleapis.com/02/c8/90/398607d91adc90/US9319047.pdf)
- [Automated synthesis of compact crossbars for sneak-path based in-memory computing](https://ieeexplore.ieee.org/document/7927093)

## License
    Copyright 2020-2021 University of Central Florida

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.