# Aerodynamic Shape Optimisation
This repository contains an example case for shape optimisation using Eilmer as the CFD solver and the python package pyOptsparse for the optimisation process. The flow simulation results and meshes of the final optimisation cycle, lua files for geometry generation and flow configurations as well as domain sketches is included.

### Prerequisites
We will be using [Eilmer](https://github.com/gdtk-uq/gdtk?tab=readme-ov-file) a well known hypersonic CFD solver to simulate the flow and PSQP from [PyOptsparse](https://github.com/mdolab/pyoptsparse/blob/main/README.md) to run the optimisation cycles. Make sure to install the prerequisites software for Eilmer from gdtk before installing it.

## Optimisation Cycle 

### Geometry Creation and Mesh Generation

to execute the lua file to output the svg file of the current iteration
```
dofile("sketch-domain.lua")
```

### Setting Configuration for Solver



example for the steady state solver
```
-- output settings
config.print_count = 50

SteadyStateSolver{
   use_preconditioner = true,
   precondition_matrix_type = "ilu",
   ilu_fill = 0,
   frozen_preconditioner_count = 20,
   
   use_scaling = true,
   use_complex_matvec_eval = true,
   use_physicality_check = true,
   
   number_total_steps = 5000,
   stop_on_relative_global_residual = 1.0e-12,

   -- Settings for FGMRES iterative solver
   max_outer_iterations = 80,
   max_restarts = 4,

   residual_based_cfl_scheduling = true,
   cfl_max = 1e4,

   -- Settings for start-up phase
   number_start_up_steps = 10,
   cfl0 = 0.5,
   eta0 = 0.01,
   sigma0 = 1.0e-50,

   -- Settings for inexact Newton phase
   cfl1 = 1.0,
   sigma1 = 1.0e-50,
   eta1 = 0.01,
   tau1 = 0.5,
   p1 = 0.7,

   -- Settings control write-out
   snapshots_count = 50,
   number_total_snapshots = 10,
   write_diagnostics_count = 20,
   write_loads_count = 20,
}
```

### Optimiser

## Final Result
![Final Optimised Inlet](https://github.com/abhx7/Aerodynamic-Shape-Optimisation/blob/main/Hypersonic%20Inlet%20-%201%20Parameter/rho-plot.png)
