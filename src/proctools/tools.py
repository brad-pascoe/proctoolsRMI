from proctools.strain_setup import StrainProfile


def get_case_folders(path: str,strain_profile=None):
    import re
    import os
    import numpy as np

    if strain_profile is None:
        directory = path
    else:
        directory = os.path.join(path,str(strain_profile))
    if not os.path.exists(directory):
        print("Directory doesn't exist")
        print(directory)
        return None

    case_names = [case for case in os.listdir(directory) if 'S' in case]
    strain_values = [float(re.findall(r'(?<=S).+',os.path.basename(case))[0]) for case in case_names]
    order = np.flip(np.argsort(strain_values))
    cases = [(os.path.join(directory,case_names[i]),strain_values[i]) for i in order]
    return cases


def find_file(folder: str, time: float, prefix: str = '', suffix: str = '') -> str:
    import os
    import re

    if not os.path.exists(folder):
        print(f'Folder {folder} not found')
        return None
    file_list = [os.path.join(folder,file) for file in os.listdir(folder) if (match := re.search(fr'(?<={prefix})[\+\-\d\.]+(?={suffix})',file)) if float(match[0]) == time]
    if len(file_list) > 1:
        print(f'Multiple matches found in folder {folder} at time {time}')
        return None
    elif len(file_list) == 0:
        print(f'No matches found in folder {folder} at time {time}')
        file_list = [file for file in os.listdir(folder) if (match := re.search(f'(?<={prefix}).+(?={suffix})',file))]
        file_list = [file for file in os.listdir(folder)]
        # print(file_list)
        return None
    else:
        return file_list[0]


def get_convergence_cases(path: str, pattern: str = None) -> list[(str,int)]:
    import os
    import re
    import numpy as np
    if pattern is None:
        cases = [x for x in os.listdir(path)]
        cells = [int(x) for x in cases]
    else:
        cases = [x for x in os.listdir(path) if pattern in x]
        cells = [int(match[0]) for x in cases if (match := re.search(r'\d+',x)) is not None]

    order = np.argsort(cells)
    cases = [(os.path.join(path,cases[i]),cells[i]) for i in order]
    return cases


def get_strain3D_cases(path: str, sim_details_path: str = None) -> list[tuple[str,StrainProfile,str,float,float]]:
    import os
    import pandas as pd

    sim_details_file = "SimDetails.csv"
    if sim_details_path is not None:
        sim_details_file = os.path.join(sim_details_path,sim_details_file)
    if not os.path.exists(sim_details_file):
        print(f"Looking for file that does not exist: {sim_details_file}")
        quit()
    sim_details = pd.read_csv(sim_details_file,index_col='Label', skipinitialspace=True)
    sim_names = sim_details.index.tolist()
    folders = os.listdir(path)
    cases = []
    for sim in sim_names:
        if sim not in folders:
            continue
        number,label,SA,ST = sim_details.loc[sim]
        cases.append((os.path.join(path,sim),sim,label,SA,ST))

    return cases
