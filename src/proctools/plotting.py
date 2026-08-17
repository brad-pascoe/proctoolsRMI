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


def _resolve_axis(target: plt.Axes | str) -> plt.Axes:
    return plt.figure(target).gca() if isinstance(target, str) else target


def plot_series(
    target: plt.Axes | str,
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    i: int,
    *,
    color: str | None = None,
    marker: bool = True,
    linestyle: str = "-",
    linewidth: float = 1.5,
    label: str | None = None,
    offset: float = 0.0,
    spacing: float = 0.15,
    **kwargs,
) -> None:
    ax = _resolve_axis(target)
    plot_kwargs = dict(
        label=label,
        color=color if color is not None else colour_array[i],
        linestyle=linestyle,
        linewidth=linewidth,
    )
    if marker:
        plot_kwargs["marker"] = marker_array[i]
        plot_kwargs["markevery"] = (0.1 + offset, spacing)
    plot_kwargs.update(kwargs)
    ax.plot(dataframe[x_var], dataframe[y_var], **plot_kwargs)


def plot_theory(
    target: plt.Axes | str,
    dataframe: pd.DataFrame,
    x_var: str,
    y_var: str,
    i: int,
    *,
    color: str = "k",
    linestyle: str = "--",
    linewidth: float = 1.25,
    **kwargs,
) -> None:
    """Reference/theory line sharing marker i with its matching plot_series call."""
    plot_series(
        target, dataframe, x_var, y_var, i,
        color=color, linestyle=linestyle, linewidth=linewidth, **kwargs,
    )
