from pathlib import Path
from proctools.strain_setup import StrainProfile


def get_case_folders(path: str | Path,strain_profile=None):
    import re
    import numpy as np

    path = Path(path)
    if strain_profile is None:
        directory = path
    else:
        directory = path/str(strain_profile)
    if not directory.exists():
        print("Directory doesn't exist")
        print(directory)
        return None

    case_names = [entry.name for entry in directory.iterdir() if 'S' in entry.name]
    strain_values = [float(re.findall(r'(?<=S).+',case)[0]) for case in case_names]
    order = np.flip(np.argsort(strain_values))
    cases = [(directory/case_names[i],strain_values[i]) for i in order]
    return cases


def find_file(folder: str | Path, time: float, prefix: str = '', suffix: str = '') -> Path | None:
    import re

    folder = Path(folder)
    if not folder.exists():
        print(f'Folder {folder} not found')
        return None
    file_list = [file for file in folder.iterdir() if (match := re.search(fr'(?<={prefix})[\+\-\d\.]+(?={suffix})',file.name)) if float(match[0]) == time]
    if len(file_list) > 1:
        print(f'Multiple matches found in folder {folder} at time {time}')
        return None
    elif len(file_list) == 0:
        print(f'No matches found in folder {folder} at time {time}')
        file_list = [file for file in folder.iterdir() if (match := re.search(f'(?<={prefix}).+(?={suffix})',file.name))]
        file_list = [file for file in folder.iterdir()]
        # print(file_list)
        return None
    else:
        return file_list[0]


def get_convergence_cases(path: str | Path, pattern: str = None) -> list[tuple[Path,int]]:
    import re
    import numpy as np
    path = Path(path)
    if pattern is None:
        cases = [entry.name for entry in path.iterdir()]
        cells = [int(x) for x in cases]
    else:
        cases = [entry.name for entry in path.iterdir() if pattern in entry.name]
        cells = [int(match[0]) for x in cases if (match := re.search(r'\d+',x)) is not None]

    order = np.argsort(cells)
    cases = [(path/cases[i],cells[i]) for i in order]
    return cases


def get_strain3D_cases(path: str | Path, sim_details_path: str | Path | None = None) -> list[tuple[Path,str,StrainProfile,float,float]]:
    import pandas as pd

    path = Path(path)
    sim_details_file = Path("SimDetails.csv")
    if sim_details_path is not None:
        sim_details_file = Path(sim_details_path)/sim_details_file
    if not sim_details_file.exists():
        print(f"Looking for file that does not exist: {sim_details_file}")
        quit()
    sim_details = pd.read_csv(sim_details_file,index_col='Label', skipinitialspace=True)
    sim_names = sim_details.index.tolist()
    folders = [entry.name for entry in path.iterdir()]
    cases = []
    for sim in sim_names:
        if sim not in folders:
            continue
        number,label,SA,ST = sim_details.loc[sim]
        cases.append((path/sim,sim,label,SA,ST))

    return cases
