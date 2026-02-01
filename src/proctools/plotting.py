import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

marker_array = ["o", "s", "^", "D", "*", "P", "X", "v", ".", "p"]
colour_array = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]
CB_color_cycle = [
    "#377eb8",
    "#ff7f00",
    "#4daf4a",
    "#f781bf",
    "#a65628",
    "#984ea3",
    "#999999",
    "#e41a1c",
    "#dede00",
]
CB_color_cycle = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#f781bf",
    "#a65628",
    "#984ea3",
    "#999999",
    "#e41a1c",
    "#dede00",
]
# "#A2142F",
JFM_dpi = 1200
JFM_dpi_adj = 900


def set_standard_figure_details() -> None:
    matplotlib.rcParams["font.family"] = "sans-serif"
    # matplotlib.rcParams['figure.figsize'] = (3.75, 3.5)
    matplotlib.rcParams["figure.figsize"] = (5, 3)
    matplotlib.rcParams["font.size"] = 12
    matplotlib.rcParams["legend.fontsize"] = 10  # 8.5
    # plt.rcParams.update({
    # "mathtext.fontset": "stix",
    # "font.family": "STIXGeneral"
    # })
    matplotlib.rc("font", **{"family": "sans-serif", "sans-serif": ["Helvetica"]})
    plt.rcParams.update(
        {
            "text.usetex": True,
            # "font.family": "serif",
            # "text.latex.preamble": r"\usepackage{amsmath}"
            "text.latex.preamble": r"\usepackage{txfonts}",
        }
    )
    # "font.family": "serif",
    # matplotlib.rcParams["figure.autolayout"] = True
    # matplotlib.pyplot.rcParams['figure.constrained_layout.use'] = True


def change_figure_size(plotname: str, width: float, height: float) -> None:
    import matplotlib.pyplot as plt

    plt.figure(plotname).set_figheight(height)
    plt.figure(plotname).set_figwidth(width)


def set_presentation_figure_details() -> None:
    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["figure.figsize"] = (5, 4)
    matplotlib.rcParams["font.size"] = 14
    matplotlib.rcParams["legend.fontsize"] = 12  # 8.5
    matplotlib.rcParams["figure.autolayout"] = True


def plot_colour(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    plotname: str,
    i: int,
    label_string=None,
    linestyle: str = "-",
    linewidth: float = 1.5,
    offset: float = 0,
    *args,
    **kwargs,
) -> None:
    # if offset == 0:
    #     offset = i/100
    plt.figure(plotname)
    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        label=label_string,
        marker=marker_array[i],
        markevery=(0.1 + offset, 0.12 + offset),
        color=colour_array[i],
        linestyle=linestyle,
        # markersize=5,
        linewidth=linewidth,
        *args,
        **kwargs,
    )


def plot_colour2(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    plotname: str,
    i: int,
    label: str = None,
    linestyle: str = "-",
    linewidth: float = 1.25,
    marker: bool = True,
    length_mult: int = 1.0,
    *args,
    **kwargs,
) -> None:
    plt.figure(plotname)
    if marker:
        kwargs["marker"] = marker_array[i]
        if length_mult == 0:
            kwargs["markevery"] = (0.10 + 0.03 * i, 0.125)
        else:
            L = int(len(dataframe) / length_mult)
            increment = (L * 12) // 100
            start = (L * (10 + 3 * i)) // 100
            kwargs["markevery"] = (start, increment)
        # kwargs['markevery'] = (0.10+0.02*i,0.15)
        kwargs["markersize"] = 6

    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        label=label,
        color=CB_color_cycle[i],
        linestyle=linestyle,
        # markersize=5,
        linewidth=linewidth,
        *args,
        **kwargs,
    )


def plot_axis_colour(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    axis: str,
    i: int,
    label_string=None,
    linestyle: str = "-",
    offset: float = 0,
    spacing=0.15,
    *args,
    **kwargs,
) -> None:
    axis.plot(
        dataframe[x_var],
        dataframe[y_var],
        label=label_string,
        marker=marker_array[i],
        markevery=(0.1 + offset, spacing),
        color=colour_array[i],
        linestyle=linestyle,
        *args,
        **kwargs,
    )


def subplot_colour(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    axes,
    i: int,
    label_string=None,
    linestyle: str = "-",
    offset: float = 0,
    *args,
    **kwargs,
) -> None:
    axes.plot(
        dataframe[x_var],
        dataframe[y_var],
        label=label_string,
        marker=marker_array[i],
        markevery=(0.1 + offset, 0.15),
        color=colour_array[i],
        linestyle=linestyle,
        *args,
        **kwargs,
    )


def plot_dashed_black(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    plotname: str,
    i: int,
    label_string: str = None,
    offset: float = 0,
    *args,
    **kwargs,
) -> None:
    if offset == 0:
        offset = i / 100
    plt.figure(plotname)
    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        marker=marker_array[i],
        markevery=(0.15 + offset, 0.15 + offset),
        color="k",
        linestyle="--",
        label=label_string,
        *args,
        **kwargs,
    )


def plot_black(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    plotname: str,
    i: int,
    linestyle: str = "--",
    offset: float = 0,
    *args,
    **kwargs,
) -> None:
    plt.figure(plotname)
    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        marker=marker_array[i],
        markevery=(0.2 + offset, 0.15),
        color="k",
        linestyle=linestyle,
        *args,
        **kwargs,
    )


def plot_axis_black(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    axis,
    i: int,
    linestyle: str = "--",
    offset: float = None,
    color="k",
    *args,
    **kwargs,
) -> None:
    if offset is None:
        offset = i / 100
    axis.plot(
        dataframe[x_var],
        dataframe[y_var],
        marker=marker_array[i],
        markevery=(0.2 + offset, 0.15 + 3 * i / 100),
        color=color,
        linestyle=linestyle,
        *args,
        **kwargs,
    )


def plot_dotted_black(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    plotname: str,
    i: int,
    linestyle: str = ":",
    offset: float = 0,
    *args,
    **kwargs,
) -> None:
    plt.figure(plotname)
    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        marker=marker_array[i],
        markevery=(0.2, 0.15),
        color="k",
        linestyle=linestyle,
        *args,
        **kwargs,
    )


def plot_dashed_grey(dataframe, x_var, y_var, plotname, i, label=None):
    import matplotlib.pyplot as plt

    plt.figure(plotname)
    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        marker=marker_array[i],
        markevery=(0.25, 0.15),
        color="dimgray",
        linestyle="--",
        label=label,
    )


def plot_dotdash_grey(
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    plotname: str,
    i: int,
    linestyle: str = "-.",
    offset: float = 0,
    *args,
    **kwargs,
) -> None:
    plt.figure(plotname)
    plt.plot(
        dataframe[x_var],
        dataframe[y_var],
        marker=marker_array[i],
        markevery=(0.15, 0.15),
        color="gray",
        linestyle=linestyle,
        *args,
        **kwargs,
    )
