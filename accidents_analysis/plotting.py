from typing import Tuple, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_distplot(df: pd.DataFrame,
                  x_column: str,
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
                df[df[hue_column] == x][x_column],
                hist=hist,
                kde=kde,
                kde_kws={'linewidth': 3, 'shade': True},
                label=x,
                norm_hist=norm_hist,
            )
    else:
        sns.distplot(
            df[x_column],
            hist=hist,
            kde=kde,
            kde_kws={'linewidth': 3, 'shade': True},
            norm_hist=norm_hist,
        )

    # Plot formatting
    if legend:
        plt.legend(prop={'size': 16})
    plt.title(f'Density Plot vs {hue_column}' if hue_column else 'Density Plot')
    plt.xlabel(x_column)
    plt.ylabel('Density')
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
    plt.show()


def plot_normalised_barplot(df: pd.DataFrame,
                            x_column: str,
                            hue_column: str,
                            title: str = None,
                            figsize: Tuple[int, int] = (14, 8),
                            palette: Dict = None,
                            legend: bool = True,
                            output_path: str = None):
    """
    Plots percentage of every category from hue_column in division of categories from x_column.
    """
    title = title if title else f'percentage of {hue_column} in {x_column}'
    x, y, hue = x_column, "percentage", hue_column
    normalized_df = (df[hue]
                     .groupby(df[x])
                     .value_counts(normalize=True)
                     .rename(y)
                     .reset_index())

    plt.figure(figsize=figsize)
    plt.title(title, fontweight='bold', fontsize=16)
    ax = sns.barplot(x=x, y=y, hue=hue, data=normalized_df, palette=palette)
    for p in ax.patches:
        ax.annotate(
            format(p.get_height(), '.2f'),
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center',
            va='center',
            xytext=(0, 10),
            textcoords='offset points'
        )
    if legend:
        plt.legend(loc="upper right", bbox_to_anchor=(1, 1))
    else:
        ax.get_legend().set_visible(False)
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
    plt.show()


def plot_countplot(df: pd.DataFrame,
                   x_column: str,
                   hue_column: str = None,
                   title: str = None,
                   figsize: Tuple[int, int] = (14, 8),
                   palette: Dict = None,
                   output_path: str = None):
    """
    Plots count plot.
    """
    title = title if title else f'Count of {x_column}'

    plt.figure(figsize=figsize)
    plt.title(title, fontweight='bold', fontsize=16)
    sns.countplot(x=x_column, y=None, hue=hue_column, data=df, palette=palette)
    plt.xticks(rotation=90, fontsize=10, fontweight='bold')
    plt.xlabel(x_column, fontsize=14)
    plt.ylabel('count', fontsize=14)

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')

    plt.tight_layout()
    plt.show()
