import sys, os
#GDTKINST = os.path.expandvars("$HOME/gdtkinst")
#sys.path.append(GDTKINST)

import shlex, subprocess, string, math
import numpy
from pyoptsparse import SLSQP, Optimization
from pyoptsparse import PSQP

def run_command(cmdText):
    """
    Run the command as a subprocess.
    """
    # Flush before using subprocess to ensure output
    # text is in the right order.
    sys.stdout.flush()
    if (type(cmdText) is list):
        args = cmdText
    else:
        args = shlex.split(cmdText)
    print("\n About to run cmd:", " ".join(args))
    return subprocess.check_call(args)
    
def prepare_input_script(params):
    """
    Prepare the actual input file for Eilmer4 from a template
    which has most of the Lua input script in place and just
    a few place-holders that need to be substituted for actual
    values.
    """
    substituteDict = {"r1x":params[0]}
    fp = open("inlet.template.lua", 'r')
    text = fp.read()
    fp.close()
    template = string.Template(text)
    text = template.substitute(substituteDict)
    fp = open("inlet.lua", 'w')
    fp.write(text)
    fp.close()
    return

def run_simulation(params):
    #improvement can be to modify function to call bash file to make new directory to store the results of each iteration
    
    run_command('prep-gas ideal-air.inp ideal-air-gas-model.lua')
    prepare_input_script(params)
    run_command('e4shared --prep --job=inlet')
    
    run_command('e4-nk-shared --job=inlet --verbosity=1')
    #for parallel computation
    #run_command('mpirun -np 16  e4-nk-dist --snapshot-start=last --job=inlet')# | tee -a log.txt')

    run_command('e4shared --post --job=inlet --tindx-plot=all \
         --add-vars="mach,total-p" --vtk-xml')
    #post processing
    run_command('e4shared --post --job=inlet --tindx-plot=last'+
                ' --add-vars="mach,total-p"'+
	        ' --slice-list="1,$,:,0"'+ #not sure till wha index is outlet height 
                ' --output-file=profile.data')
                
def objfunc(params):
        global c;
        print('\nIteration Number ',c,'\n')
        c+=1
        
        #convert it back to an array
        params = params["var"]
	
        funcs={}
        #try:
        run_simulation(params)
        
        p0_inl = 32.73 #Pa calcualte properly
        data = numpy.loadtxt("profile.data", skiprows=1)
        ys = data[:,1] # remember that Python array indices start at 0
        n = len(ys)
        p0_inf = max(data[:,19])
        print("\np_total=", p0_inf, "total_pressure_ratio=", p0_inl/p0_inf)
        obj= 1 - (p0_inl/p0_inf)
        funcs["obj"] = obj
	#space out all the outputs so everything is understandable when running
        print("\nparameters = ", params, "\nobj = ", obj)
        fail = False
        
        return funcs, fail

run_command('rm -rf flow grid hist loads plot solid config limiter-values residuals ramp-ref-residuals.saved gm-*.lua rr-*.lua log.txt e4-nk.diagnostics.dat')

if 0:
	print("Let's run a simulation.")
	params =  [0.5]
	run_simulation(params)
if 0:	
        #c=0
	print("Run 0")
	print("Evaluate objective function.")
	params =  [0.5]
	objv = objfunc(params)

#----------------------------------------Optimisation-------------------------------------------
if 1:
	print("Let the optimizer take control and run the numerical experiment.")

	params = [0.5]#, 0.05]
	c = 0 #iteration count	

	# Optimization Object
	optProb = Optimization("Shape Optimisation - Hypersonic Inlet", objfunc)

	# Design Variables
	optProb.addVarGroup("var", 1, lower=[0.0], upper=[1.05], value=params)

	# Objective
	optProb.addObj("obj")
	# Check optimization problem
	print(optProb)


	# Optimizer
	psqp = PSQP(params)
	psqp.setOption('IPRINT', 1)
	psqp.setOption('IFILE', 'psqp.out')
	psqp.setOption('XMAX', 1e-02)
	psqp.setOption('MIT', 20)
	psqp.setOption('MFV', 10)
	psqp.setOption('MET', 1)
	psqp.setOption('MEC', 1)


	sol=psqp(optProb, sens="FD", storeHistory='psqp_hist.hst')
	print(sol)
	print("optimised params from paper: ",[0.3615196, 0.0422752, 0.35])


