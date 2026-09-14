import numpy as np
import seaborn.objects as so

from soplot._errors import FigureModifyError, UnexpectedTypeError
from soplot._stats import Agg
from soplot._types import AkwArgs, Args, KwArgs, arg_initializer

"""
Seaborn Objects Api Objects
"""


class SoPlot(AkwArgs):
    """
    SoPlot object constructor.

    ex:
    SoPlot(data = df, x = 'tips', color = 'total_bill')

    <AAKwArgs>
    Args:
        *args, data=None, x=None, y=None, color=None, alpha=None, fill=None, marker=None,
        pointsize=None, stroke=None, linewidth=None, linestyle=None, fillcolor=None, fillalpha=None,
        edgewidth=None, edgestyle=None, edgecolor=None, edgealpha=None, text=None, halign=None,
        valign=None, offset=None, fontsize=None, xmin=None, xmax=None, ymin=None, ymax=None,
        group=None)
        https://seaborn.pydata.org/generated/seaborn.objects.Plot.html
    """
    ...


# design,
# layer (Add) params 
# Mark, Stat , Move, kwargs 
class SoLayer(AkwArgs):
    """ Specify a layer of the visualization in terms of mark and data transform(s).
    
        ex:
        SoLayer(so.Bars(), so.Hist(), so.Dodge(), legent = True)

        Args:
            (mark, *transforms, orient=None, legend=True, label=None, data=None, **variables)
            Arguments of seaborn.objects.Plot.add:
            https://seaborn.pydata.org/generated/seaborn.objects.Plot.add.html
    """
    ...


class MDF:
    """

    Represents seaborn object modifiers.
    Scale, Facet, Label, Pair, Layout

    """

    class Modifier:
        """Base of every modifier below.

        Membership used to be decided by a substring match on the class
        qualname, which any class with ``MDF`` in its name passed. Inheriting a
        marker makes the check exact and cheap: ``isinstance(mdf, MDF.Modifier)``.
        """

    class Scale(Modifier, KwArgs):
        """

        Specify mappings from data units to visual properties.

        ex:
        So.Scale(y = 'log', color= so.Continuous("ch:.2").tick(upto=4).label(unit=""))

        Args:
            ** keyword arguments: https://seaborn.pydata.org/generated/seaborn.objects.Plot.scale.html
        """
        ...

    class Facet(Modifier, KwArgs):
        """Produce subplots with conditional subsets of the data.

        ex:
        So.Facet(col = 'sex', row = 'varies')


        Args:
            (col=None, row=None, order=None, wrap=None): https://seaborn.pydata.org/generated/seaborn.objects.Plot.facet.html
        """
        ...

    class Pair(Modifier, KwArgs):
        """

        Produce subplots by pairing multiple x and/or y variables.

        ex:
        So.Pair(x = 'tip', y = 'total_bill', wrap = 3)


        Args:
            (x=None, y=None, wrap=None, cross=True): https://seaborn.pydata.org/generated/seaborn.objects.Plot.pair.html
        """
        ...

    class Layout(Modifier, KwArgs):
        """Control the figure size and layout.

        ex:
        So.Layout(size = (3,3), engine = 'constrained')

        Args:
            (*, size=<default>, engine=<default>, extent=<default>: https://seaborn.pydata.org/generated/seaborn.objects.Plot.layout.html
        """
        ...

    class Label(Modifier, KwArgs):
        """ Controls the labels and titles for axes, legends, and subplots.

        ex:
        So.Label(title = 'sales', legend = True)

        Args:
            (*, title=None, legend=None, **variables): https://seaborn.pydata.org/generated/seaborn.objects.Plot.label.html
        """

    class Limit(Modifier, KwArgs):
        """Control the range of visible data.


        ex:
        So.Limit(x=(0, 4), y=(-1, 6))

        Args:
            (**limits): https://seaborn.pydata.org/generated/seaborn.objects.Plot.limit.html
        """
        ...

    class Share(Modifier, KwArgs):
        """Control sharing of axis limits and ticks across subplots.

        ex:
        So.Share(x="col", y="row") also True and False

        Args:
             (**shares): https://seaborn.pydata.org/generated/seaborn.objects.Plot.share.html
        """
        ...

    class Theme(Modifier, Args):
        """Control the appearance of elements in the plot.

        ex: Arg of dicts
        So.Theme({"axes.facecolor": "w", "axes.edgecolor": "slategray"}),
        So.Theme(style.library["fivethirtyeight"]),
        So.Theme(axes_style("whitegrid") | plotting_context("talk"));

        Args:
            (config, /)
            https://seaborn.pydata.org/generated/seaborn.objects.Plot.theme.html
            Matplotlib rc parameters:
            https://matplotlib.org/stable/tutorials/introductory/customizing.html
        """
        ...


"""
Custom plots with so.Plot() api 
"""


class SO:
    @staticmethod
    def add_layers(plot: so.Plot, *layers: SoLayer):
        """Add each layer to ``plot``, in the order given.

        Args:
            plot: The plot to add to.
            *layers: Layers to add. A falsy layer -- ``None``, say -- is skipped.

        Returns:
            A new plot carrying the layers. ``so.Plot`` is immutable, so the
            argument is left untouched.
        """
        for lyr in layers:
            if lyr:
                plot = plot.add(*lyr.args, **lyr.kwargs)
        return plot

    @staticmethod
    def modify_plot(plot: so.Plot, *modifiers: MDF):
        """Apply each modifier to ``plot`` according to its type.

        ``MDF.Scale`` becomes ``plot.scale(...)``, ``MDF.Facet`` becomes
        ``plot.facet(...)``, and so on; an ``MDF.Theme`` is applied entry by
        entry. An empty modifier is a no-op, which is how the builders below
        say "nothing to apply here".

        Args:
            plot: The plot to modify.
            *modifiers: ``MDF`` modifiers.

        Returns:
            A new plot carrying the modifiers. ``so.Plot`` is immutable, so the
            argument is left untouched.

        Raises:
            UnexpectedTypeError: A non-empty modifier is not an ``MDF`` type.
        """

        # An empty container carries no setting, and the builders below pass one
        # (``KwArgs()``) as their "no modifier here" placeholder, so only a
        # non-empty object of a foreign type is an error.
        foreign = [type(mdf).__name__ for mdf in modifiers
                   if mdf and not isinstance(mdf, MDF.Modifier)]
        if foreign:
            raise UnexpectedTypeError('Expected an MDF modifier', received=foreign)

        for mdf in modifiers:
            if isinstance(mdf, MDF.Scale):
                plot = plot.scale(**mdf)
            elif isinstance(mdf, MDF.Facet):
                plot = plot.facet(**mdf)
            elif isinstance(mdf, MDF.Pair):
                plot = plot.pair(**mdf)
            elif isinstance(mdf, MDF.Layout):
                plot = plot.layout(**mdf)
            elif isinstance(mdf, MDF.Label):
                plot = plot.label(**mdf)
            elif isinstance(mdf, MDF.Limit):
                plot = plot.limit(**mdf)
            elif isinstance(mdf, MDF.Share):
                plot = plot.share(**mdf)
            elif isinstance(mdf, MDF.Theme) and mdf:  # an empty theme sets nothing
                for m in mdf:
                    plot = plot.theme(m)

        return plot

    @staticmethod
    def compare_plot(data, variable, features, sub_figures, **kwargs):
        """Plot ``variable`` against each feature, one feature per subfigure.

        Each subplot shares ``variable`` on the base axis and carries one
        feature on the other, so the subfigures read as one comparison. Nothing
        is returned: every plot is drawn onto the subfigure it was given.

        Args:
            data: The data frame every subplot reads from.
            variable: The column held constant on the base axis.
            features: One column per subplot, matched with ``sub_figures``.
            sub_figures: Matplotlib subfigures, an array or a single one.

            **kwargs:
                layers: ``Args`` of ``Args`` of ``SoLayer``, one entry per
                    feature; the last entry repeats once the entries run out.
                    Each ``SoLayer`` needs a real mark -- an empty one cannot be
                    added to a plot.
                modifiers: ``Args`` of ``Args`` of ``MDF``, one entry per
                    feature, applied after the global ones.
                global_modifiers: ``MDF`` modifiers applied to every subplot.
                plot_vars: ``Args`` of ``KwArgs``, extra plot variables
                    (``color``, ``marker``, ...) injected per feature.
                base: ``'x'`` or ``'y'`` -- which axis ``variable`` sits on.
        """
        #default parameters
        kw_args = KwArgs(layers=Args(Args(SoLayer())), 
                         modifiers=Args(Args()), 
                         global_modifiers=Args(KwArgs()), 
                         base='x',
                         plot_vars=Args(KwArgs()),
                        )
        #override by provided parameters
        kw_args = kw_args | kwargs
        kw_args = KwArgs(**kw_args)

        features_length = len(features)
        # inistialize arguments to same length
        kw_args['layers'] = arg_initializer(kw_args['layers'], Args(SoLayer()), features_length)
        kw_args['modifiers'] = arg_initializer(kw_args['modifiers'], Args(), features_length)
        kw_args['global_modifiers'] = arg_initializer(
            kw_args['global_modifiers'], KwArgs(), features_length
        )
        kw_args['plot_vars'] = arg_initializer(kw_args['plot_vars'], KwArgs(), features_length)
        #determine axis
        axis = 'x' if kw_args['base'] == 'x' else 'y'
        other_axis = 'x' if axis == 'y'  else 'y'
        #set axis to plot data
        plot_param = SoPlot(data=data)
        plot_param.kwargs[other_axis] = variable
        kw_args['plot_param'] = plot_param
        kw_args['axis'] = axis
        kw_args['other_axis'] = other_axis
        #modifies all plots with seaborn.object modifiers
        global_modifiers = kw_args['global_modifiers']
        #make sure subfigures are iterable
        sub_figures = _as_sequence(sub_figures)
        for idx_, (feature_, sub_figure_) in enumerate(zip(features, sub_figures)):
            #set axis for each feature plot
            kw_args['plot_param'].kwargs[kw_args['axis']] = variable
            kw_args['plot_param'].kwargs[kw_args['other_axis']] = feature_
            #inject grouping plot parameters
            kw_args['plot_param'].kwargs.update(**kw_args['plot_vars'][idx_])
            #mark and transform objecsts for each plot as array
            layers = kw_args['layers'][idx_]
            #override global modifiers for each plot
            modifiers = kw_args['modifiers'][idx_]
            ppl = so.Plot(*kw_args['plot_param'].args, **kw_args['plot_param'].kwargs)
            ppl = SO.add_layers(ppl, *layers)
            ppl = SO.modify_plot(ppl, *global_modifiers)
            ppl = SO.modify_plot(ppl, *modifiers)
            #publish plot on subfigure-uses default plot theme overriding rc subplot parameters
            ppl.on(sub_figure_).plot()

    @staticmethod
    def multi_outlier_box(data, features, sub_figures, **kwargs):
        """Draw one outlier box per feature, optionally paired with a histogram.

        With ``show_hist`` the subfigure is split in two: on ``axis='x'`` the
        histogram sits above the box, otherwise beside it, with its tick labels
        switched off so the pair reads as one panel. Nothing is returned;
        everything is drawn onto the subfigures given.

        Args:
            data: The data frame every subplot reads from.
            features: One column per subplot, matched with ``sub_figures``.
            sub_figures: Matplotlib subfigures, an array or a single one.

            **kwargs:
                axis: ``'x'`` or ``'y'`` -- which axis the feature sits on.
                box_vars: ``Args`` of ``KwArgs``, arguments forwarded to
                    :meth:`outlier_box` per feature.
                hist_vars: ``Args`` of ``KwArgs``, arguments forwarded to
                    :meth:`histogram` per feature.
                modifiers: ``Args`` of ``Args`` of ``MDF``, applied to both the
                    histogram and the box of that feature.
                show_hist: ``Args`` of booleans, one per feature.
        """

        kw_args = KwArgs(
            axis='x',
            box_vars=Args(KwArgs()),
            hist_vars=Args(KwArgs()),
            modifiers=Args(Args()),
            show_hist=Args(False)
        )
        kw_args = kw_args | kwargs
        kw_args = KwArgs(**kw_args)

        #
        kw_args['box_vars'][0]['axis'] = kw_args['axis']
        kw_args['hist_vars'][0]['axis'] = kw_args['axis']

        #

        features_length = len(features)
        kw_args['box_vars'] = arg_initializer(kw_args['box_vars'], KwArgs(), features_length)
        kw_args['hist_vars'] = arg_initializer(kw_args['hist_vars'], KwArgs(), features_length)
        kw_args['modifiers'] = arg_initializer(kw_args['modifiers'], Args(), features_length)
        kw_args['show_hist'] = arg_initializer(kw_args['show_hist'], False, features_length)

        sub_figures = _as_sequence(sub_figures)
        for idx_, (feature_, sub_figure) in enumerate(zip(features, sub_figures)):
            his_fig = None
            box_fig = None
            his_theme = MDF.Theme()
            box_theme = MDF.Theme()

            if kw_args['show_hist'][idx_]:

                his = SO.histogram(data=data, feature=feature_, **kw_args['hist_vars'][idx_])

                if kw_args['axis'] == 'x':
                    # hist on top, box on bottom
                    # disable his xticklabel
                    # disable hist title
                    # disable hist yticklabel
                    ss_figs = sub_figure.subfigures(2, 1)
                    his_fig = ss_figs[0]  # hist on top
                    box_fig = ss_figs[1]
                    # no tick labels on the histogram: the box below carries them
                    his_theme = MDF.Theme(
                        {'xtick.labelbottom': False, 'ytick.labelleft': False}
                    )

                else:
                    ss_figs = sub_figure.subfigures(1, 2)
                    his_fig = ss_figs[1]  # hist on right
                    box_fig = ss_figs[0]
                    # no tick labels on the histogram: the box beside it carries them
                    his_theme = MDF.Theme(
                        {'xtick.labelbottom': False, 'ytick.labelleft': False}
                    )

                his = SO.modify_plot(his, his_theme)  # apply hist theme
                his = SO.modify_plot(his, *kw_args['modifiers'][idx_])  # overriding modifiers
                his.on(his_fig).plot(pyplot=True)
                his_fig.axes[0].set_xlabel('')
                his_fig.axes[0].set_ylabel('')
            else:
                box_fig = sub_figure

            box = SO.outlier_box(data=data, feature=feature_, **kw_args['box_vars'][idx_])
            box = SO.modify_plot(box, box_theme)  # apply box theme
            box = SO.modify_plot(box, *kw_args['modifiers'][idx_])  # global modifiers

            box.on(box_fig).plot(pyplot=True)

    @staticmethod
    def histogram(data, feature, **kwargs):
        """Build a histogram of ``feature``, with a KDE curve over it.

        Args:
            data: The data frame to read from.
            feature: The column to count.
            **kwargs:
                axis: ``'x'`` or ``'y'`` -- which axis the feature sits on.
                hist_layer: The counting layer. Defaults to proportion bars.
                kde_layer: The density layer, or ``None`` for bars alone.
                modifiers: ``Args`` of ``MDF`` applied to the finished plot.

        Returns:
            An ``so.Plot``. It is not drawn yet -- call ``.on(...).plot()``.
        """
        kw_args = KwArgs(
            axis='x',
            hist_layer=SoLayer(so.Bars(), so.Hist('proportion')),
            kde_layer=SoLayer(so.Area(), so.KDE()),
            modifiers=Args()
        )
        kw_args = kw_args | kwargs
        kw_args = KwArgs(**kw_args)

        plot_param = SoPlot(data=data)
        plot_param.kwargs[kw_args['axis']] = feature
        kw_args['plot_param'] = plot_param

        hst = so.Plot(*kw_args['plot_param'].args, **kw_args['plot_param'].kwargs) \
            .add(*kw_args['hist_layer'].args, **kw_args['hist_layer'].kwargs)
        if kw_args['kde_layer'] is not None:
            hst = hst.add(*kw_args['kde_layer'].args, **kw_args['kde_layer'].kwargs)

        hst = SO.modify_plot(hst, *kw_args['modifiers'])

        return hst

    @staticmethod
    def outlier_box(data, feature, **kwargs):
        """Build a box-like summary of ``feature``: the sample and its bounds.

        The plot carries the observations themselves plus five reference marks:
        the interquartile range, the two whisker bounds
        (:class:`soplot._stats.Agg`), the mean and the median. The feature is
        laid out against a constant dummy column, which is what gives the marks
        a single row to sit on.

        Args:
            data (pd.DataFrame): data frame
            feature (str): feature name\n
            **kwargs: 
                axis = 'x',
                datapoint_var = KwArgs(),
                dummy_name = '',
                percentiles = Args(25.0,75.0),
                dot_var  = KwArgs(pointsize=0.5),
                jitter_var  = KwArgs(width=0.5),
                dash_var= KwArgs(alpha=.4),
                dodge_var = KwArgs(gap = .8),
                quartile_var  = KwArgs(color='k',linewidth=15),
                i_quartile_var  = KwArgs(color='r',linewidth=5),
                mean_line_var = KwArgs(color='red',linestyle='--'),
                median_line_var = KwArgs(color='k',linestyle = ':'),
                band_view = False,
                modifiers = Args()

        Returns:
            An ``so.Plot``. It is not drawn yet -- call ``.on(...).plot()``.
        """
        kw_args = KwArgs(
            axis='x',
            datapoint_var=KwArgs(),
            dummy_name='',
            percentiles=Args(25.0, 75.0),
            dot_var=KwArgs(pointsize=0.5),
            jitter_var=KwArgs(width=0.5),
            dash_var=KwArgs(alpha=.4),
            dodge_var=KwArgs(gap=.8),
            quartile_var=KwArgs(color='k', linewidth=15),
            i_quartile_var=KwArgs(color='r', linewidth=5),
            mean_line_var=KwArgs(color='red', linestyle='--'),
            median_line_var=KwArgs(color='k', linestyle=':'),
            band_view=False,
            modifiers=Args()
        )
        # override params

        kw_args = kw_args | kwargs
        kw_args = KwArgs(**kw_args)

        plot_param = SoPlot(data=data)
        plot_param.kwargs[kw_args['axis']] = feature
        other_axis = 'y' if kw_args['axis'] == 'x' else 'x'
        kw_args['dummy_data'] = np.full(data.shape[0], kw_args['dummy_name'])
        plot_param.kwargs[other_axis] = kw_args['dummy_data']
        kw_args['plot_param'] = plot_param

        base_layer = SoLayer(
            so.Dot(**kw_args['dot_var']),
            so.Jitter(**kw_args['jitter_var']),
            **kw_args['datapoint_var'],
        )
        if kw_args['band_view']:
            base_layer = SoLayer(
                so.Dash(**kw_args['dash_var']),
                so.Dodge(**kw_args['dodge_var']),
                **kw_args['datapoint_var'],
            )

        sp = so.Plot(*kw_args['plot_param'].args, **kw_args['plot_param'].kwargs) \
            .add(*base_layer.args, **base_layer.kwargs) \
            .add(so.Range(**kw_args['quartile_var']), so.Perc(kw_args['percentiles'])) \
            .add(so.Dash(**kw_args['i_quartile_var']), so.Agg(Agg.upper_outlier_bound)) \
            .add(so.Dash(**kw_args['i_quartile_var']), so.Agg(Agg.lower_outlier_bound)) \
            .add(so.Dash(**kw_args['mean_line_var']), so.Agg('mean')) \
            .add(so.Dash(**kw_args['median_line_var']), so.Agg('median'))
        sp = SO.modify_plot(sp, *kw_args['modifiers'])

        return sp


def _as_sequence(sub_figures):
    """Return ``sub_figures`` as something that can be iterated feature by feature.

    ``Figure.subfigures`` hands back an array for a grid and a bare subfigure
    for a single cell; both have to read the same way here.
    """
    if hasattr(sub_figures, 'flatten'):
        return sub_figures.flatten()
    if isinstance(sub_figures, np.ndarray):
        return sub_figures
    return [sub_figures]


def add_barlabel(figure):
    """Label every bar of a drawn figure with its value.

    Takes the matplotlib figure, not the seaborn plotter: draw first with
    ``so.Plot(...).on(fig).plot(pyplot=True)``, then pass ``fig``.

    The mark has to be ``so.Bar()``. ``so.Bars()`` leaves matplotlib no bar
    containers to read, so nothing is labelled -- and nothing is raised either.

    Args:
        figure: A matplotlib figure that has already been drawn on.

    Returns:
        The same figure, with a label on every bar.

    Raises:
        FigureModifyError: The figure could not be read or labelled. The
            original error is kept as the cause.
    """
    try:
        axes = figure.figure.axes
        for axis in axes:
            for container in axis.containers:
                axis.bar_label(container)
        return figure
    except Exception as exc:
        raise FigureModifyError(
            'Barlabel could not be added to the figure',
            hint='Mark object must be Bar() instead of Bars()',
        ) from exc
     
