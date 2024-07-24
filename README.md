# Aerodynamic Shape Optimisation
This repository contains an example case for 2D shape optimisation using Eilmer as the CFD solver and the python package pyOptsparse for the optimisation process. The flow simulation results and meshes of the final optimisation cycle, lua files for geometry generation and flow configurations as well as domain sketches is included.

The example case is replicating the setup in the paper [Shape optimization of a hypersonic inlet using a new clustering-based hybrid optimizer](https://arc.aiaa.org/doi/epdf/10.2514/6.2023-3055)

### Prerequisites
We will be using [Eilmer](https://github.com/gdtk-uq/gdtk?tab=readme-ov-file) a well known hypersonic CFD solver to simulate the flow and PSQP from [PyOptsparse](https://github.com/mdolab/pyoptsparse/blob/main/README.md) to run the optimisation cycles. Make sure to install the prerequisites software (especialy the LLVM compiler) for Eilmer from gdtk documentation before installing it.

## Optimisation Cycle 
There are 2 basic iterative steps in any shape optimisation cycle:
* Flow Simulation
* Objective evaluation and Parameter Update

This loop is repeated for a maximum number of evaluations or till the objective value falls below a threshold.


In the example case, the optimisation is run through a python script and the workflow is as follows:
1. Initialise the parameters
2. Executes the commands to prepare the lua files from the template lua file for
   - Geometry Creation and Mesh Generation
   - Solver Configuration and Sketch Domain
   - Output results of flow simulation
   - Post processing to retreive data
3. Evaluate the objective function and update the parameters accordingly
4. Repeat step 2 and 3 to till a user defined maximum number of optimisation iterations


### Geometry Creation and Mesh Generation

#### Geometry
Firstly, set the parameter variables and the fixed variables for the geometry, 
```
--paramterised point
r1x=$r1x
r1y=$r1y
```
and the flow conditions like pressure, temperature and velocity to set the initial states as well as boundary conditions
```
flowstate1=FlowState:new{p=[pressure], T=[temperature], velx=[velocity in x direction]}
```
> [!NOTE]
> Substitute the values for the quantities without the brackets.

#
To define the flow domain, first establish all the points in the geometry. 
```
pnts = {
   -- Point defining the inlet
   i1 = {x=0.0, y=0.0},
   i2 = {x=0.0, y=H},
...
       }
```

#
These points can be connected using straight lines or curved lines like BSpline or Bezier curves. In this 2D case, it represents the surface of the bodies as well as the boundary domain. A line can be defined like this. 
```
ramp1 = Line:new{p0=pnts.i1,p1=pnts.r1}
```
Similarly, the documentation is available for the other kinds of lines.

If this was a 3D case, we would define surfaces for the bodies and the boundary. 

#
The lines are grouped together to create blocks that will be used for generating "patches" which Eilmer can interpret to create the required mesh. For example,
```
lines = {}
patches = {}
-- Block leading to the throat.
lines.w0 = Line:new{p0=pnts.i1, p1=pnts.i2}
lines.s0 = Polyline:new{segments={ramp1, ramp2}}
lines.n0 = Line:new{p0=pnts.i2, p1=pnts.c}
lines.e0 = Line:new{p0=pnts.rn, p1=pnts.c}
patches[0] = AOPatch:new{north=lines.n0, south=lines.s0,
                         west=lines.w0, east=lines.e0}
```
There are different sorts of patches available like CoonsPatch and AOPatch, each used depending on the kind of block.

#
Physical groups can also be defined to organize certains geometry elements like lines, points or even 2D surfaces based on the setup description like inlet, walls and farfield. 

#### Mesh
Structured meshes are created from the patches created.
```
grids = {}
grids[0] = StructuredGrid:new{psurface=patches[0],
                              niv=61, njv=31}
grids[1] = StructuredGrid:new{psurface=patches[1],
                              niv=45, njv=31}
```
> [!NOTE]
> niv and nij are the number of elements along each direction.
> 
> nik is also used for 3D cases.
> 
> Eilmer supports unstructured meshes as well. Check the documentation.

#
Each of the flow solution blocks need to be initialised.
```
-- Define the flow-solution blocks.
blks = {}
for ib=0,1 do
   blks[ib] = FluidBlock:new{grid=grids[ib], initialState=FlowState:new{...}}
end
```
We then define the block connections. For example, 
```
-- Set boundary conditions, first, connections
connectBlocks(blks[0], 'east', blks[1], 'west')
```
> [!WARNING]
> Make sure all the points, line and surfaces are defined correctly as well as the patches are created and blocks are connected correctly as in your required setup.
> 
> Any tiny errors here will cause the meshing to not happen, solver to not converge or other issues may crop up.


#
The boundary conditions are set based on the setup either individually or can be set together using a dictionary for the physical groups defined.
```
blks[0].bcList[west] = InFlowBC_Supersonic:new{flowCondition=FlowState:new{...}}
```
#


There is a seperate lua file included in the repo to output the svg file of the current iteration and is executed using the following command.
```
dofile("sketch-domain.lua")
```

### Setting Configuration for Solver

There is extensive [documentation](https://gdtk.uqcloud.net/docs/eilmer/eilmer-reference-manual/#_configuration_options) available for solver configurations to define the time-stepping, viscous effects, flux settings and output settings.

The example case is for steady state so we include the steady state solver. This is a sample configuration for steady state solver.
```
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
The PSQP optimiser is used and variables are defined for the point coordinates along with their bounds. The objective function is defined for maximum pressure recovery at the inlet. The data is retrieved from the post processing files to evaluate the objective function. A simple **Finite Difference** method is used to generate the new parameters which are updated to start the next iteration. This process is repeated till the defined maximum number of evaluations is reached.
```
sol=psqp(optProb, sens="FD", storeHistory='psqp_hist.hst')
print(sol)
 ```
A sample case for setting up the optimiser is available in [PyOptsparse documentation](https://mdolab-pyoptsparse.readthedocs-hosted.com/en/latest/quickstart.html)

## Final Result
![Final Optimised Inlet](https://github.com/abhx7/Aerodynamic-Shape-Optimisation/blob/main/Hypersonic%20Inlet%20-%201%20Parameter/rho-plot.png)
