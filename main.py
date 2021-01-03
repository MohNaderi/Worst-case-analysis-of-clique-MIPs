import tools
import formulations
import argparse
import sys
from multiprocessing import Process
import csv



def Main():
    
    parser=argparse.ArgumentParser()
    parser.add_argument("instance_name", help="determine instance name" +\
                 ", make sure the instance already exist in the directory")
 
    group=parser.add_argument_group("Formulation Type")
    FormulationType=group.add_mutually_exclusive_group(required=True)
    FormulationType.add_argument("-c", "--conflict", help="conflict model"
                                 ,action="store_true")
    FormulationType.add_argument("-s", "--sparse", help="sparse model"
                          ,action="store_true")
    FormulationType.add_argument("-sJ", "--sparseJeroslow", help="Jeroslow Extended" +\
                          "+sparse formulation",action="store_true")
    FormulationType.add_argument("-cB", "--conflictBalas", help="Balas Extended" +\
                          "+conflict",action="store_true")
 
    
    parser.add_argument("-NonDef","--Nondefault_model_setting", help="turn off" +\
                        "the gurobi default setting:cut/presolve/heuristic on"
                        , action="store_true")
    parser.add_argument("-cBPerfect","--isPerfect_cB", help="check if" +\
                        " the instance satisfies the sufficient condition for BEF formulation to be perfect"
                        , action="store_true")
    
    args=parser.parse_args()
 
            
    if args.conflict:
        C = formulations.conflict(args.instance_name)
    if args.sparse:
        C = formulations.sparse(args.instance_name)
    if args.sparseJeroslow:
        C=formulations.sparseJeroslow(args.instance_name)
    if args.conflictBalas:
        C = formulations.conflictBalas(args.instance_name)
    
    if args.Nondefault_model_setting:
        C.setModelAttr()
    
    if args.isPerfect_cB:
        graphTest=tools.Graph(inputfile=args.instance_name)
        sys.stderr.write("%s is conflictBalas Perfect: " %args.instance_name.split(".")[0])
        sys.stderr.write("%r \t" %graphTest.isconflictBalasPerfect())
    
    #solve the model with Gurobi solver
    C.solveGurobi()
            

if __name__=="__main__":
    
    #kill the process if it passes 3650 seconds
    program = Process(target=Main,args=())
    program.start()
    program.join(timeout=3650)
    program.terminate()
    
    if program.is_alive():
        with open("resultsforclique.csv",'a',newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["MC"])
