-- inlet.lua
--
config.title = "Flow into a scramjet inlet."
print("-----------------------------------------------------------")
print(config.title)

-- Gas model and flow states for simulation.
nsp, nmodes, gmodel = setGasModel('ideal-air-gas-model.lua')
print("GasModel set to ideal air. nsp= ", nsp)

-- The low_pressure_gas is an arbitrary fill condition for the blocks.
-- It will be swept away.
low_pressure_gas = FlowState:new{p=1, T=0.0024}
-- The external_stream will provide an environment for the rocket's exhaust gas.
external_stream = FlowState:new{p=1, T=0.0024, velx=6.73}
print(external_stream,'\n')

-- Define the geometry of the scramjet inlet ramp and a bit of duct following that ramp.
-- Remember that Eilmer length units are metres.

--paramterised point
r1x=0.5025023844423587
r1y=0.04031915760804584
Lc = 0.35

---inlet entry point
lw = 1.05
hw = 0.15

---outlet top exit
H = 0.2
L = 1.25

pnts = {
   -- Point defining the inlet
   i1 = {x=0.0, y=0.0},
   i2 = {x=0.0, y=H},
   -- Point defining the outlet
   o1 = {x=L, y=hw},
   o2 = {x=L, y=H},
   -- Points defining the compression-ramp surface.
   r1 = {x=r1x, y=r1y},
   rn = {x=lw, y=hw},
   -- Cowl point
   c = {x=L-Lc, y=H},
   }

ramp1 = Line:new{p0=pnts.i1,p1=pnts.r1}
ramp2 = Line:new{p0=pnts.r1,p1=pnts.rn}
--ramp=PolyLine:new{segments={pnts.i1, pnts.r1, pnts.rn}}
cowl=Line:new{p0=pnts.c, p1=pnts.o2}
 
lines = {}
patches = {}
-- Block leading to the throat.
lines.w0 = Line:new{p0=pnts.i1, p1=pnts.i2}
lines.s0 = Polyline:new{segments={ramp1, ramp2}}
lines.n0 = Line:new{p0=pnts.i2, p1=pnts.c}
lines.e0 = Line:new{p0=pnts.rn, p1=pnts.c}
patches[0] = AOPatch:new{north=lines.n0, south=lines.s0,
                         west=lines.w0, east=lines.e0}

                         
-- Block inside the cowl surface.
lines.n1 = Line:new{p0=pnts.c, p1=pnts.o2}
lines.e1 = Line:new{p0=pnts.o1, p1=pnts.o2}
lines.s1 = Line:new{p0=pnts.rn, p1=pnts.o1}
patches[1] = AOPatch:new{north=lines.n1, south=lines.s1,
                         west=lines.e0, east=lines.e1}

-- Mesh the patches, with particular discretisation.
--cfy = RobertsFunction:new{end0=true, end1=false, beta=1.01}
grids = {}
grids[0] = StructuredGrid:new{psurface=patches[0],
                              niv=61, njv=31}
grids[1] = StructuredGrid:new{psurface=patches[1],
                              niv=45, njv=31}


-- Define the flow-solution blocks.
blks = {}
for ib=0,1 do
   blks[ib] = FluidBlock:new{grid=grids[ib], initialState=low_pressure_gas}
end

-- Set boundary conditions, first, connections
connectBlocks(blks[0], 'east', blks[1], 'west')

-- then, directly specify the other boundary conditions.
blks[0].bcList[west] = InFlowBC_Supersonic:new{flowCondition=external_stream}
blks[0].bcList[north] = InFlowBC_Supersonic:new{flowCondition=external_stream}
blks[1].bcList[east] = OutFlowBC_Simple:new{}
blks[1].bcList[north] = WallBC_NoSlip_Adiabatic:new{} 
blks[0].bcList[south] = WallBC_NoSlip_Adiabatic:new{}
blks[1].bcList[south] = WallBC_NoSlip_Adiabatic:new{}


--convective flux settings
config.interpolation_order = 2
config.flux_calculator = "ausmdv"
config.freeze_limiter_on_step = 4000

config.extrema_clipping = false
config.apply_limiter = true
config.unstructured_limiter = "venkat"
config.smooth_limiter_coeff = 0.5  --config.venkat_K_value = 0.5
config.thermo_interpolator = "rhop"

-- viscous flux settings
config.viscous = true
config.spatial_deriv_locn = "cells"
config.spatial_deriv_calc = "least_squares"
config.diffuse_wall_bcs_on_init = false
config.number_init_passes = 25


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
   number_start_up_steps = 100,
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

dofile("sketch-domain.lua")
