import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Process some arguments.')

# Cards for the MadGraph run
parser.add_argument('-r', '--run'    , default="RunCards/default_LO.dat",      help='path to MG5 run card')
parser.add_argument('-P', '--proc'   ,                                         help='path to MG5 proc card')
parser.add_argument('-p', '--param'  , default="ParamCards/Higgsino",          help='path to SLHA/param card')
parser.add_argument('-y', '--pythia' , default="PythiaCards/pythia8_card.dat", help='path to pythia card')

# Options for customizing the run
parser.add_argument('-m', '--mass'   , action='append', nargs=2,               help="pass in like '-m MN1 150'")
parser.add_argument('-E', '--sqrts'  , default=13,                             help="Center of mass energy, in GeV")
parser.add_argument('-n', '--numev'  , default=10000,                          help="Number of events to process")

# Tag for this run
parser.add_argument('-t', '--tag'    , default="run",                          help='name for the job')

# Random seed for this job
parser.add_argument('-s', '--seed'   , default=0,                              help='random seed')


args = parser.parse_args()


# create a new directory for this run
try:
    os.mkdir("output")
except FileExistsError:
    pass
try:
    os.mkdir("output/%s"%args.tag)
except FileExistsError:
    print("Output name %s already used, pick another." % args.tag)
    exit

# ===========================================================================================================================
#
# Update the param card
#
newparamcard="output/"+args.tag+"/"+args.param.split("/")[-1]
newparamcardf=open(newparamcard,"w")
for line in open(args.param):
    written=False
    for part,mass in args.mass:
        if part in line:
            newparamcardf.write(line.replace(part,mass))
            written=True
            break
    if not written:
        newparamcardf.write(line)
newparamcardf.close()

#
# Update the run card
#
newruncard="output/"+args.tag+"/"+args.run.split("/")[-1]
newruncardf=open(newruncard,"w")
for line in open(args.run):
    if "ecms" in line:
        newruncardf.write(line.replace("ecms",str(float(args.sqrts)/2)))
    elif "nevents" in line:
        sline=line.split()
        sline[0]=args.numev
        newruncardf.write(' '.join(sline)+"\n")
    else:
        newruncardf.write(line)
newruncardf.close()

#
# Copy the proc card
#
shutil.copyfile(args.proc,"output/"+args.tag+"/"+args.proc.split("/")[-1])
# ===========================================================================================================================


# ===========================================================================================================================
#
# Create the madgraph configuration card
#
mg5config=open("output/"+args.tag+"/"+"run.mg5","w")

for line in open(args.proc):
    if line.strip()!="output" and line.strip()!="output -f":
        mg5config.write(line)
    else:
        mg5config.write("output PROC_%s\n" % args.tag)
    

#mg5config.write("set run_mode 0\n")  # mg5_configuration.txt
mg5config.write("launch PROC_%s\n" % args.tag)
mg5config.write("shower=Pythia8\n")
mg5config.write("madspin=OFF\n")
mg5config.write("reweight=OFF\n")
mg5config.write(newparamcard.split("/")[-1]+"\n")
mg5config.write(newruncard.split("/")[-1]+"\n")
mg5config.write("set iseed %d\n" % args.seed)
mg5config.write("done\n")
    
mg5config.close()
# ===========================================================================================================================


