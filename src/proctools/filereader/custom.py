from pathlib import Path
import pandas as pd


def load_pressure_fluc(folder: str | Path,time2tau: float = 1) -> pd.DataFrame:
    pressure_filename = "simulation_pressure.dat"
    pressure_cols = ["Time", "PMin","PMax","PDiff"]
    pressure_file = Path(folder)/pressure_filename
    pressure_data = pd.read_fwf(pressure_file,header=None,names=pressure_cols)
    pressure_data["Tau"] = pressure_data["Time"]*time2tau
    return pressure_data


def load_pressure_data(folder: str | Path,time2tau: float = 1) -> pd.DataFrame:
    pressure_filename = "Simulation_Pressure.dat"
    pressure_cols = ["Time", "Mean","RMS"]
    pressure_file = Path(folder)/pressure_filename
    pressure_data = pd.read_fwf(pressure_file,header=None,names=pressure_cols)
    pressure_data["Tau"] = pressure_data["Time"]*time2tau
    return pressure_data


def load_KL_data(folder: str | Path, rmiparameters=None) -> pd.DataFrame:
    KL_filename = "simulation_KL.dat"
    KL_cols = ["Time", "K_mag","L_mag","W","beta"]
    KL_file = Path(folder)/KL_filename
    KL_data = pd.read_fwf(KL_file,header=None,names=KL_cols,usecols=range(5))
    if rmiparameters is not None:
        KL_data['Tau'] = KL_data['Time']*rmiparameters.time2tau
        KL_data['L'] = KL_data['L_mag']/rmiparameters.lambda_bar
        KL_data['W'] /= rmiparameters.lambda_bar
    return KL_data


def load_JacVolMass_data(folder: str | Path) -> pd.DataFrame:
    JVM_filename = "Error_JacVolMass.dat"
    JVM_cols = ["Iteration","Time", "Jacobian","Volume","Mass"]
    JVM_file = Path(folder)/JVM_filename
    JVM_data = pd.read_fwf(JVM_file,header=None,names=JVM_cols,usecols=range(5))
    return JVM_data


def load_error_norm_data(folder: str | Path, variable: str) -> pd.DataFrame:
    error_filename = f"ErrorNorm_{variable}.dat"
    error_file = Path(folder)/error_filename
    error_cols = ["Iteration","Time","L0","L1","L2"]

    error_data = pd.read_fwf(error_file,header=None,names=error_cols)
    return error_data


def load_tecplot(file,onedimension=False,convert_to_dataframe=False):
    import re
    import numpy as np
    import pandas as pd

    with open(file,"r") as fileCon:

        variables = []
        domains = 0
        solution_array = []

        while (True):
            line = fileCon.readline().strip()
            if len(line) == 0:
                break
            elif 'VARIABLES' in line:
                variables, line = find_variables(fileCon)
                iNVar = len(variables)

            if 'ZONE' not in line:
                print(f"Was expecting a line with ZONE, got: {line}")

            iCells, jCells, kCells = get_cell_counts(line)

            # Read next line of just DT=(
            line = fileCon.readline()
            # Read double lines
            for i in range(iNVar):
                line = fileCon.readline().strip()
                if not re.match('DOUBLE',line):
                    print("Error reading tecplot file")
            # Read next line of just )
            line = fileCon.readline()

            # Read array
            temp_solution_array = np.zeros(shape=(kCells,jCells,iCells,iNVar))
            for k in range(kCells):
                for j in range(jCells):
                    for i in range(iCells):
                        line = fileCon.readline()
                        matches = re.findall(r'(?<=\s)\S+(?=\s)',line)
                        temp_solution_array[k,j,i,:] = matches

            if onedimension:
                temp_solution_array = temp_solution_array[0,0,:,:]
                if domains == 0:
                    solution_array = temp_solution_array
                else:
                    solution_array = np.concatenate((solution_array,temp_solution_array))
            else:
                print('Three dimensions')
                solution_array.append(temp_solution_array)
            domains += 1

    # print(f"Found {domains} domains")
    if (convert_to_dataframe):
        solution_array = pd.DataFrame(solution_array, columns=variables)

    return solution_array


def find_variables(fileCon):
    import re
    variables = []
    # Read variable list
    while (True):
        line = fileCon.readline().strip()
        if re.search('ZONE',line):
            break
        variable_match = re.search('(?<=").+(?=")',line)
        variables.append(variable_match[0])

    return (variables,line)


def get_cell_counts(line):
    import re
    i_match = re.search(r'(?<=I=)\s*\d+',line)
    iCells = int(i_match[0])
    j_match = re.search(r'(?<=J=)\s*\d+',line)
    jCells = int(j_match[0])
    k_match = re.search(r'(?<=K=)\s*\d+',line)
    kCells = int(k_match[0])
    return (iCells,jCells,kCells)
