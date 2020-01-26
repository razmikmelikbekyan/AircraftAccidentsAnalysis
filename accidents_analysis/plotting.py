from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_distplot(df: pd.DataFrame,
                  plotting_column: str,
                  hue_column: str = None,
                  norm_hist: bool = False,
                  hist: bool = False,
                  kde: bool = True,
                  legend: bool = True,
                  figsize: Tuple[int, int] = (10, 6),
                  output_path: str = None):
    """Plots distribution of given column."""
    plt.figure(figsize=figsize)
    if hue_column:
        for x in df[hue_column].unique():
            sns.distplot(
                df[df[hue_column] == x][plotting_column],
                hist=hist,
                kde=kde,
                kde_kws={'linewidth': 3, 'shade': True},
                label=x,
                norm_hist=norm_hist,
            )
    else:
        sns.distplot(
            df[plotting_column],
            hist=hist,
            kde=kde,
            kde_kws={'linewidth': 3, 'shade': True},
            norm_hist=norm_hist,
        )

    # Plot formatting
    if legend:
        plt.legend(prop={'size': 16})
    plt.title(f'Density Plot vs {hue_column}' if hue_column else 'Density Plot')
    plt.xlabel(plotting_column)
    plt.ylabel('Density')
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
    plt.show()
