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
        valign=None, offset=None, fontsize=None, xmin=None, xmax=None, ymin=None, ymax=None, group=None): https://seaborn.pydata.org/generated/seaborn.objects.Plot.html
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
            (mark, *transforms, orient=None, legend=True, label=None, data=None, **variables ):  Arguments of seaborn.objects.Plot.add :https://seaborn.pydata.org/generated/seaborn.objects.Plot.add.html#
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
            (config, /):https://seaborn.pydata.org/generated/seaborn.objects.Plot.theme.html  Matplotlib rc parameters are documented on the following page: https://matplotlib.org/stable/tutorials/introductory/customizing.html
        """
        ...


"""
Custom plots with so.Plot() api 
"""


class SO:
    @staticmethod
    def add_layers(plot: so.Plot, *layers: SoLayer):
        """
        Adds given layers to the given plot
        Args:
            plot:
            *layers:

        Returns:

        """
        for lyr in layers:
            if lyr:
                plot = plot.add(*lyr.args, **lyr.kwargs)
        return plot

    @staticmethod
    def modify_plot(plot: so.Plot, *modifiers: MDF):
        """_summary_

        Args:
            plot (so.Plot): _description_

        Returns:
            _type_: _description_
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
            elif isinstance(mdf, MDF.Theme):
                if mdf:  # apply only if not empty
                    for m in mdf:
                        plot = plot.theme(m)

        return plot

    @staticmethod
    def cross_plot(data,variables, features, sub_figures,**kwargs):     
        kw_args = KwArgs(layers=Args(Args(SoLayer())), 
                         modifiers=Args(Args()), 
                         global_modifiers=Args(KwArgs()), 
                         base='x',
                         plot_vars=Args(KwArgs()),
                        )
        kw_args = kw_args | kwargs
        kw_args = KwArgs(**kw_args) 

    @staticmethod
    def compare_plot(data, variable, features, sub_figures, **kwargs):
        """_summary_

        Args:
            data (_type_): _description_
            variable (_type_): _description_
            features (_type_): _description_
            sub_figures (_type_): _description_

            **kwargs:
                layers = Args( Args( SoLayer() ) ): _description_
                modifiers = Args( Args( MDF ) ): _description_
                global_modifiers = Args( MDF ): _description_
                plots_vars = Args(KwArgs())
                base = 'x'
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
        kw_args['global_modifiers'] = arg_initializer(kw_args['global_modifiers'], KwArgs(), features_length)
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
        sub_figures = sub_figures.flatten() if hasattr(sub_figures, 'flatten') else sub_figures if isinstance(sub_figures, np.ndarray) else [sub_figures]
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
    def multi_histogram(data, features, sub_figures, **kwargs):
        """_summary_ TODO

        Args:
            data (_type_): _description_
            features (_type_): _description_
            sub_figures (_type_): _description_
        """
        pass

    @staticmethod
    def multi_outlier_box(data, features, sub_figures, **kwargs):
        """_summary_

        Args:
            data (_type_): _description_
            features (_type_): _description_
            sub_figures (_type_): _description_

            kw_args = KwArgs(
                axis = 'x'
                box_vars = Args(KwArgs()) : _description_
                hist_vars = Args(KwArgs()): _description_
                modifiers = Args(Args()) : _description_
                show_hist = Args(False) : _description_
            )
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

        sub_figures = sub_figures.flatten() if hasattr(sub_figures, 'flatten') else sub_figures if isinstance(sub_figures,
                                                                                                                np.ndarray) else [
            sub_figures]
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
                    his_theme = MDF.Theme({'xtick.labelbottom': False, 'ytick.labelleft': False, })  # disable hist yticklabel #disable hist title

                else:
                    ss_figs = sub_figure.subfigures(1, 2)
                    his_fig = ss_figs[1]  # hist on right
                    box_fig = ss_figs[0]
                    his_theme = MDF.Theme({'xtick.labelbottom': False, 'ytick.labelleft': False, })  # disable hist yticklabel #disable hist title
                    # box_theme = MDF.Theme({'xtick.labelbottom':False,'ytick.labelleft':False,}) #disable hist yticklabel #disable hist title

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
        """_summary_

        Args:
            data (_type_): _description_
            feature (_type_): _description_
            **kwargs
                axis = 'x',
                hist_layer = So.Layer(so.Bars(),so.Hist('proportion')),
                kde_layer = So.Layer(so.Area(),so.KDE()),
                modifiers = Args()

        Returns:
            _type_: _description_
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
        """_summary_

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

        base_layer = SoLayer(so.Dot(**kw_args['dot_var']), so.Jitter(**kw_args['jitter_var']), **kw_args['datapoint_var'])
        if kw_args['band_view']:
            base_layer = SoLayer(so.Dash(**kw_args['dash_var']), so.Dodge(**kw_args['dodge_var']), **kw_args['datapoint_var'])

        sp = so.Plot(*kw_args['plot_param'].args, **kw_args['plot_param'].kwargs) \
            .add(*base_layer.args, **base_layer.kwargs) \
            .add(so.Range(**kw_args['quartile_var']), so.Perc(kw_args['percentiles'])) \
            .add(so.Dash(**kw_args['i_quartile_var']), so.Agg(Agg.upper_outlier_bound)) \
            .add(so.Dash(**kw_args['i_quartile_var']), so.Agg(Agg.lower_outlier_bound)) \
            .add(so.Dash(**kw_args['mean_line_var']), so.Agg('mean')) \
            .add(so.Dash(**kw_args['median_line_var']), so.Agg('median'))
        sp = SO.modify_plot(sp, *kw_args['modifiers'])

        return sp


def add_barlabel(figure):
    """
    This function adds bar labels to a barplot.
    designed for plots created with seaborn objects api interface
    make sure that the used Mark object is Bar() instead of Bars() 
    Parameters

    plotobject : barplot
    numberoflayers : int
    """
    try:
        axes = figure.figure.axes
        for i,ax  in enumerate(axes):
            ax0 = ax
            ax0_containers = ax0.containers
            for j , cont in enumerate(ax0_containers):
                ax0.bar_label(cont)
        return figure
    except Exception as exc:
        raise FigureModifyError(
            'Barlabel could not be added to the figure',
            hint='Mark object must be Bar() instead of Bars()',
        ) from exc
     
