from typing import Tuple, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_countplot(df: pd.DataFrame,
                   x_column: str,
                   hue_column: str = None,
                   title: str = None,
                   figsize: Tuple[int, int] = (14, 8),
                   palette: Dict = None,
                   color: str or List[str] = "darkorange",
                   ylims: Tuple = None,
                   ticks_rotation: int = 90,
                   ticks_fontsize: int = 10,
                   output_path: str = None):
    """Plots count plot."""
    title = title if title else f'Count of {x_column}'

    plt.figure(figsize=figsize)
    plt.title(title, fontweight='bold', fontsize=16)
    splot = sns.countplot(x=x_column, hue=hue_column, data=df, palette=palette, color=color)
    for p in splot.patches:
        splot.annotate(
            f'{p.get_height():,.0f}',
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center',
            va='center' if ticks_rotation == 0 else 'bottom',
            xytext=(0, 10),
            textcoords='offset points',
            fontweight='bold',
            rotation=ticks_rotation,
            fontsize=ticks_fontsize
        )
    plt.xticks(rotation=ticks_rotation, fontsize=ticks_fontsize, fontweight='bold')
    plt.yticks(fontsize=ticks_fontsize, fontweight='bold')
    plt.xlabel(x_column, fontsize=12, fontweight='bold')
    plt.ylabel('count', fontsize=12, fontweight='bold')

    if ylims:
        plt.ylim(*ylims)

    sns.despine()
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')

    plt.tight_layout()
    plt.show()


def plot_aggregated_barplot(df: pd.DataFrame,
                            x_column: str,
                            y_column: str,
                            aggregation_type: str = None,
                            hue_column: str = None,
                            hue_dict: Dict = None,
                            color: str or List[str] = 'darkorange',
                            title: str = None,
                            figsize: Tuple[int, int] = (14, 8),
                            ylims: Tuple = None,
                            ticks_rotation: int = 90,
                            ticks_fontsize: int = 10,
                            annotation_precision: int = 0,
                            output_path: str = None):
    """Plots aggregated numerical column versus categories."""

    def hue_aggregation():
        df_agg = (
            df.groupby([x_column, hue_column]).agg({y_column: aggregation_type}).reset_index()
        )
        df_agg = pd.concat(
            [df_agg[[x_column, hue_column]], df_agg.loc[:, pd.IndexSlice[:, aggregation_type]]],
            axis=1
        )
        df_agg.columns = df_agg.columns.droplevel(1)
        return df_agg

    if hue_column:
        df_aggregated = hue_aggregation()
        title = title if title else f'{aggregation_type} {y_column} by {x_column}'
    elif aggregation_type:
        df_aggregated = df.groupby(x_column).agg({y_column: aggregation_type}).reset_index()
        title = title if title else f'{aggregation_type} {y_column} by {x_column}'
    else:
        df_aggregated = df
        title = title if title else f'{y_column} by {x_column}'

    plt.figure(figsize=figsize)
    plt.title(title, fontweight='bold', fontsize=16)
    splot = sns.barplot(
        x=x_column,
        y=y_column,
        hue=hue_column,
        data=df_aggregated,
        palette=hue_dict,
        color=color
    )
    sns.despine()

    for p in splot.patches:
        splot.annotate(
            f'{p.get_height():,.{annotation_precision}f}',
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center',
            va='center' if ticks_rotation == 0 else 'bottom',
            xytext=(0, 10),
            textcoords='offset points',
            fontweight='bold',
            rotation=ticks_rotation,
            fontsize=ticks_fontsize
        )

    plt.xticks(rotation=ticks_rotation, fontsize=ticks_fontsize, fontweight='bold')
    plt.yticks(fontsize=ticks_fontsize, fontweight='bold')
    plt.xlabel(x_column, fontsize=12, fontweight='bold')
    plt.ylabel(y_column, fontsize=12, fontweight='bold')
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')

    if ylims:
        plt.ylim(*ylims)

    plt.tight_layout()
    plt.show()


def plot_lineplot(df: pd.DataFrame,
                  x_column: str,
                  y_column: str,
                  hue_column: str = None,
                  hue_dict: Dict = None,
                  color: str or List[str] = 'darkorange',
                  title: str = None,
                  figsize: Tuple[int, int] = (14, 8),
                  ticks_rotation: int = 90,
                  ticks_fontsize: int = 10,
                  output_path: str = None):
    title = title if title else f'{y_column} over {x_column}'

    plt.figure(figsize=figsize)
    plt.title(title, fontweight='bold', fontsize=16)
    sns.lineplot(
        x=x_column,
        y=y_column,
        hue=hue_column,
        data=df,
        palette=hue_dict,
        color=color,
    )
    sns.despine()

    plt.xticks(rotation=ticks_rotation, fontsize=ticks_fontsize, fontweight='bold')
    plt.yticks(fontsize=ticks_fontsize, fontweight='bold')
    plt.xlabel(x_column, fontsize=12, fontweight='bold')
    plt.ylabel(y_column, fontsize=12, fontweight='bold')
    plt.grid(True, axis='both', linestyle='--', color='gray')

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
    plt.tight_layout()
    plt.show()


def plot_normalised_barplot(df: pd.DataFrame,
                            x_column: str,
                            hue_column: str,
                            title: str = None,
                            figsize: Tuple[int, int] = (14, 8),
                            palette: Dict = None,
                            legend: bool = True,
                            ylims: Tuple = None,
                            ticks_rotation: int = 90,
                            ticks_fontsize: int = 10,
                            output_path: str = None):
    """
    Plots percentage of every category from hue_column in division of categories from x_column.
    """
    title = title if title else f'percentage of {hue_column} in {x_column}'
    x, y, hue = x_column, "percentage", hue_column
    normalized_df = (df[hue_column]
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
            va='center' if ticks_rotation == 0 else 'bottom',
            xytext=(0, 10),
            textcoords='offset points',
            fontweight='bold',
            rotation=ticks_rotation,
            fontsize=ticks_fontsize
        )
    sns.despine()

    if legend:
        plt.legend(loc="upper right", bbox_to_anchor=(1, 1))
    else:
        ax.get_legend().set_visible(False)

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')

    plt.xticks(rotation=ticks_rotation, fontsize=ticks_fontsize, fontweight='bold')
    plt.yticks(fontsize=ticks_fontsize, fontweight='bold')
    plt.xlabel(x, fontsize=12, fontweight='bold')
    plt.ylabel(y, fontsize=12, fontweight='bold')

    if ylims:
        plt.ylim(*ylims)

    plt.tight_layout()
    plt.show()


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


def plot_category_split_plot(df: pd.DataFrame,
                             figsize: Tuple[int, int] = (12, 6),
                             title: str = None,
                             x_label: str = None,
                             ticks_rotation: int = 90,
                             ticks_fontsize: int = 12,
                             output_path: str = None):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)

    if title:
        plt.title(title, fontsize=14, fontweight='bold')
    df.plot(ax=ax, kind='bar', stacked=True, rot=0,
            color=sns.color_palette('tab10', n_colors=10))
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format(x * 100) for x in vals])
    ax.set_axisbelow(True)
    sns.despine()
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.xticks(rotation=ticks_rotation, fontsize=12, fontweight='bold')
    plt.yticks(fontsize=12, fontweight='bold')
    if x_label:
        plt.xlabel(x_label, fontsize=ticks_fontsize, fontweight='bold')
    plt.ylabel('Percentage', fontsize=12, fontweight='bold')

    plt.grid(True, axis='y', linestyle='--', color='orange')
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')

    plt.show()
