# PowerSleuth

PowerSleuth is a tool that profiles your applications power/performance and phase behvior. 

See [uart/power_sleuth][] for more information.

## Prerequisites

### General

PowerSleuth is built around ScarPhase. See [scarphase][] for more instructions.

## Quick Start

#### 1. Install ScarPhase
    git clone https://github.com/uart/scarphase.git
    
    cd scarphase
    git submodule update --init

    cmake .
    make

#### 2. Install PowerSleuth
    git clone https://github.com/uart/powersleuth.git
    cd powersleuth
    
    export PYTHONPATH=/path/to/scarphase
    

## Usage

### Help

    ./powersleuth -h
    usage: ./powersleuth <command> [<args>]

    Commands:
       profile      Profile stuff
       plot         Plot power and performance data
       dump         Dump power and performance data
       show         Show stuff
       raw-dump     Dump raw performance counter data
       simpoint     Find simpoints
       refine       Refine data
       raw-plot     Plot raw performance counter data

    See './powersleuth help <command>' for more information.

### 1. Profile  

This profiles and finds runtime phases in gcc from SPEC2006, with input 166.i. The profile is saved in *gcc.profile* and is used in the succeeding examples to plot and dump gcc's phases.

    ./powersleuth profile \
        --scarphase-conf configs/scarphase/example0.conf \
        --counter-conf configs/intel/nehalem/i7-920.counters.json \
        --counter-limit=3 \
        gcc.profile \
        -- /path/to/gcc 166.i -o 166.s
     
* `./powersleuth profile` - scarphase command
* `--scarphase-conf configs/scarphase/example0.conf` - contains the configuration settings for the ScarPhase library.
* `--counter-conf configs/counters/list0.json` - a list of performance counter to sample
* `--counter-limit` - number of available hardware performance counters
* `gcc.profile` - output file
* `-- gcc 166.i -o 166.s` - command to run (use absolute paths)
        
### 2. Plot results

This plots the performance data and the detected phases from the example above.

    ./powersleuth plot power-heatmap --cpu-info configs/intel/nehalem/i7-920.cfg --profile-frequency 2.4 -t 0 gcc.profile
    
* `./scarphase plot` - scarphase command
* `power-heatmap` - subcommand: plots power heatmap
* `--cpu-info configs/intel/nehalem/i7-920.cfg` - config for the processor
* `--profile-frequency 2.4` - the frequency the profiling was done at
* `-t 0` - which thread
* `gcc.profile` - profile from example 1

![gcc/166](http://www.it.uu.se/research/group/uart/measurement/online_phase_detection/gcc-screenshot-power.png "gcc/166 screenshot")

## Publications using PowerSleuth

#### 2012
*    **Power-Sleuth: A Tool for Investigating your Program's Power Behavior** Vasileios Spiliopoulos, Andreas Sembrant and Stefanos Kaxiras. *In International Symposium on Modeling, Analysis and Simulation of Computer and Telecommunication Systems (MASCOTS'12)*


[scarphase]: https://github.com/uart/scarphase
[libscarphase]: https://github.com/uart/libscarphase
[boost]: http://www.boost.org/
[protobuf]: https://code.google.com/p/protobuf/

[numpy]: http://www.numpy.org/
[scipy]: http://www.scipy.org/
[scikit-learn]: http://scikit-learn.org/stable/
[matplotlib]: http://matplotlib.org/

[prettytable]: https://code.google.com/p/prettytable/
[progressbar]: https://code.google.com/p/python-progressbar/

[uart]: http://www.it.uu.se/research/group/uart/
[uart/power_sleuth]: http://www.it.uu.se/research/group/uart/modeling/power_modeling/power_sleuth
[uart/online-phase-detection]: http://www.it.uu.se/research/group/uart/measurement#online_phase_detection
