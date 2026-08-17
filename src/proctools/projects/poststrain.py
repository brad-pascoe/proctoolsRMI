import re
from pathlib import Path


def get_mesh_cases(data_dir: str | Path, exclude_list: list[str] | None = None) -> list[tuple[Path,str]]:
    exclude_list = exclude_list or []
    data_dir = Path(data_dir)

    mesh_dirs = [
        (entry, re.search('Mesh(.+)',entry.name)[1])
        for entry in data_dir.iterdir()
        if 'Mesh' in entry.name and not any(excl in entry.name for excl in exclude_list)
    ]

    return sorted(mesh_dirs)


def get_cell_count(case_dir: str | Path) -> int | None:
    import re
    cell_dict = {'A': 128, 'B': 256, 'C': 512}
    cell_match = re.search('Mesh([A-C])',str(case_dir))
    if cell_match:
        return cell_dict.get(cell_match.group(1))
    return None
