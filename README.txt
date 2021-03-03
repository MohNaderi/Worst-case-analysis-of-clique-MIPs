# Codes for "Worst-case analysis of clique MIPs" by Mohammad Javad Naderi, Austin Buchanan, Jose L. Walteros
Paper is available here:
http://www.optimization-online.org/DB_HTML/2021/01/8198.html

Running the code via python interpreter
=============

**********
Use python version >=3.9
**********

**********
Update gurobi to the latest version (now 9.1.1)
**********

**********
Get Worst-case-analysis-of-clique-MIPs codes from 
https://github.com/MohNaderi/Worst-case-analysis-of-clique-MIPs.git
**********

**********
Providing path to Worst-case-analysis-of-clique-MIPs codes
**********


If the codes and graphs are stored at C:\users then for the following provide help information
::
C:\Users>python main.py -h


positional arguments:
instance_name determine instance name, make sure the instance already exist in the directory

optional arguments:
-h, --help show this help message and exit
-NonDef, --Nondefault_model_setting
turn off the gurobi default setting:cut/presolve/heuristic
-cBPerfect, --isPerfect_cB
check if the instance satisfies the sufficient condition for cB formulation to be perfect

Formulation Type:
-c, --conflict conflict model
-s, --sparse sparse model
-sJ, --sparseJeroslow
Jeroslow Extended+sparse formulation
-cB, --conflictBalas Balas Extended+conflict



**********
An example 
**********
::
python main.py adjnoun.graph.txt -cB -NonDef

This command line produces csv file: "resultsforclique.csv" in your repository
