import os


def get_final_cases() -> list[tuple[str,str,int]]:
    data_dir = "/mnt/HardDrive/StrainMixing/CompressionDNS/Data/"

    case_names = ["Base", "Compression", "Sutherlands", "Plasma"]
    case_cells = [f"{x}" for x in (1024, 1024, 512, 512)]
    # case_cells = [f"{x}" for x in (512, 512, 512, 512)]

    cases = []

    for name, cells in zip(case_names, case_cells):
        case_dir = os.path.join(data_dir,name,cells)
        if os.path.exists(case_dir):
            cases.append((name, case_dir, cells))
        else:
            print(f"Dir not found for {name}.\nMissing: {case_dir}")
    return cases


def get_IWPCTM_cases() -> list[tuple[str,str,int]]:
    data_dir = "/mnt/HardDrive/CompressionDNS/data/"

    case_names = ["Base", "Compression", "Plasma"]
    case_cells = [f"{x}" for x in (1024, 1024, 512)]
    case_labels = [r"B-$\mu$T$^{0}$",r"C-$\mu$T$^{0}$"r"C-$\mu$T$^{5/2}$"]

    cases = []

    for name, cells, label in zip(case_names, case_cells, case_labels):
        case_dir = os.path.join(data_dir,name,cells)
        if os.path.exists(case_dir):
            cases.append((name, case_dir, cells))
        else:
            print(f"Dir not found for {name}.\nMissing: {case_dir}")
    return cases
