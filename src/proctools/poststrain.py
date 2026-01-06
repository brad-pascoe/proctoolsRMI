import os
import re


def get_mesh_cases(data_dir: str, exclude_list: list[str] | None = None) -> list[str]:
    exclude_list = exclude_list or []

    mesh_dirs = [
        (os.path.join(data_dir, name), re.search('Mesh(.+)',name)[1])
        for name in os.listdir(data_dir)
        if 'Mesh' in name and not any(excl in name for excl in exclude_list)
    ]

    return sorted(mesh_dirs)


def get_cell_count(case_dir: str) -> int | None:
    import re
    cell_dict = {'A': 128, 'B': 256, 'C': 512}
    cell_match = re.search('Mesh([A-C])',case_dir)
    if cell_match:
        return cell_dict.get(cell_match.group(1))
    return None
