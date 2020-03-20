import logging
import numpy
import bokeh
# import pdb

from cmath import phase, pi
from copy import deepcopy
from sympy import oo
# from bokeh.io import vform
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.models import BoxSelectTool
from bokeh.models import (HoverTool, BoxZoomTool, PanTool, WheelZoomTool,
                          ResetTool, SaveTool, TapTool,)
from bokeh.models.widgets import Button
# from bokeh.models.widgets import Toggle
from bokeh.plotting import figure
from bokeh.events import ButtonClick
from bokeh.layouts import column

from loom.misc import get_splits_with_overlap


def get_spectral_network_bokeh_plot(
    spectral_network_data, plot_range=None,
    plot_joints=False, plot_data_points=False, plot_on_cylinder=False,
    plot_two_way_streets=False,
    soliton_tree_data=None,
    plot_width=800, plot_height=800,
    notebook=False,
    slide=False,
    logger_name=None,
    marked_points=[],
    without_errors=False,
    download=False,
):
    logger = logging.getLogger(logger_name)

    if without_errors is True:
        spectral_networks = [
            sn for sn in spectral_network_data.spectral_networks
            if len(sn.errors) == 0
        ]
    else:
        spectral_networks = spectral_network_data.spectral_networks

    if len(spectral_networks) == 0:
        raise RuntimeError(
            'get_spectral_network_bokeh_plot(): '
            'No spectral network to plot.'
        )

    sw_data = spectral_network_data.sw_data

#    x_min = min([min([min([z.real for z in s_wall.z])
#                      for s_wall in sn.s_walls])
#                 for sn in spectral_networks])
#    x_max = max([max([max([z.real for z in s_wall.z])
#                      for s_wall in sn.s_walls])
#                 for sn in spectral_networks])
#    y_min = min([min([min([z.imag for z in s_wall.z])
#                      for s_wall in sn.s_walls])
#                 for sn in spectral_networks])
#    y_max = max([max([max([z.imag for z in s_wall.z])
#                      for s_wall in sn.s_walls])
#                 for sn in spectral_networks])
#    if plot_range is None:
#        # Need to maintain the aspect ratio.
#        range_min = min(x_min, y_min)
#        range_max = max(x_max, y_max)
#        plot_x_range = plot_y_range = (range_min, range_max)
#    else:
#        plot_x_range, plot_y_range = plot_range
    plot_x_range, plot_y_range = plot_range
    y_min, y_max = plot_y_range

    # Setup tools.
    hover = HoverTool(
        tooltips=[
            ('name', '@label'),
            ('root', '@root'),
        ]
    )

    # Data source for phases
    phases_ds = ColumnDataSource({
        'phase': [],
    })
    for sn in spectral_networks:
        sn_phase = '{:.3f}'.format(sn.phase / pi)
        phases_ds.data['phase'].append(sn_phase)

    # Data source containing all the spectral networks
    # XXX: changed this type of data because of problems with slider 
    # all_networks_ds = ColumnDataSource({
    #     'spectral_networks': [],
    # })
    all_networks_ds = []

    # 1. Prepare a bokeh Figure.
    bokeh_figure = figure(
        tools='pan,wheel_zoom,box_zoom,reset,save,hover,tap',
        plot_width=plot_width,
        plot_height=plot_height,
        title=None,
        x_range=plot_x_range,
        y_range=plot_y_range,
    )
    bokeh_figure.grid.grid_line_color = None

    # 2. Now add to the figure all parts of the plot that ARE NOT updated
    # by the slider widget (in case there is more than one network to plot)

    # Data source for marked points, which are drawn for an illustration.
    mphases_ds = ColumnDataSource(
        {'x': [], 'y': [], 'color': [], 'label': [], 'root': []}
    )
    for mp in marked_points:
        z, color = mp
        mphases_ds.data['x'].append(z.real)
        mphases_ds.data['y'].append(z.imag)
        mphases_ds.data['color'].append(color)
        mphases_ds.data['label'].append('')
        mphases_ds.data['root'].append('')
    bokeh_figure.circle(
        x='x', y='y', size=5, color='color', source=mphases_ds,
    )

    # Data source for punctures.
    pphases_ds = ColumnDataSource({'x': [], 'y': [], 'label': [], 'root': []})
    for pp in (sw_data.regular_punctures + sw_data.irregular_punctures):
        if pp.z == oo:
            continue
        pphases_ds.data['x'].append(pp.z.real)
        pphases_ds.data['y'].append(pp.z.imag)
        pphases_ds.data['label'].append(str(pp.label))
        pphases_ds.data['root'].append('')
    bokeh_figure.circle(
        'x', 'y', size=10, color="#e6550D", fill_color=None,
        line_width=3, source=pphases_ds,
    )

    # Data source for branch points & cuts.
    bphases_ds = ColumnDataSource({'x': [], 'y': [], 'label': [], 'root': []})
    for bp in sw_data.branch_points:
        if bp.z == oo:
            continue
        bphases_ds.data['x'].append(bp.z.real)
        bphases_ds.data['y'].append(bp.z.imag)
        bphases_ds.data['label'].append(str(bp.label))
        root_label = ''
        for root in bp.positive_roots:
            root_label += str(root.tolist()) + ', '
        bphases_ds.data['root'].append(root_label[:-2])

    bcurrent_ds = ColumnDataSource({'xs': [], 'ys': []})
    for bl in sw_data.branch_points + sw_data.irregular_singularities:
        y_r = (2j * y_max) * complex(sw_data.branch_cut_rotation)
        bcurrent_ds.data['xs'].append([bl.z.real, bl.z.real + y_r.real])
        bcurrent_ds.data['ys'].append([bl.z.imag, bl.z.imag + y_r.imag])

    bokeh_figure.x(
        'x', 'y', size=10, color="#e6550D", line_width=3, source=bphases_ds,
    )
    bokeh_figure.multi_line(
        xs='xs', ys='ys', line_width=2, color='gray', line_dash='dashed',
        source=bcurrent_ds,
    )

    plot_options_ds = ColumnDataSource(
        {'notebook': [notebook], 'show_trees': [plot_two_way_streets]}
    )

    # 3. Now add to the figure all parts of the plot that ARE updated
    # by the slider widget (in case there is more than one network to plot)

    # Data source for the current plot
    current_ds = ColumnDataSource({
        'ranges': [],
        'color': [],
        'arrow_x': [],
        'arrow_y': [],
        'arrow_angle': [],
        'label': [],
        'root': [],
        'xs': [],
        'ys': []
    })

    # Data source for plotting data points
    data_pts_ds = ColumnDataSource({
        'x': [],
        'y': [],
    }) 

    if plot_two_way_streets is True:
    # XXX: disabling this feature temporarily.
    # TO DO: Reinstate this feature later
        logger.warning(
            'Plotting of two-way streets is currently disabled.'
        )
        plot_two_way_streets = False

    if plot_two_way_streets is True:
        # all_networks_ds['spectral_networks'] is a 2-dim array,
        # where the first index chooses a spectral network
        # and the second index chooses a soliton tree
        # of the two-way streets of the spectral network.
        for i, soliton_trees in enumerate(soliton_tree_data):
            data_entry = []
            if len(soliton_trees) == 0:
                # Fill with empty data.
                empty_data = get_s_wall_plot_data(
                    [], sw_data, logger_name,
                    spectral_networks[i].phase,
                )
                data_entry.append(empty_data)
            else:
                for tree in soliton_trees:
                    tree_data = get_s_wall_plot_data(
                        tree.streets, sw_data, logger_name,
                        spectral_networks[i].phase,
                    )
                    # The first data contains all the soliton trees
                    # of the two-way streets in a spectral network.
                    if len(data_entry) == 0:
                        data_entry.append(deepcopy(tree_data))
                    else:
                        for key in tree_data.keys():
                            data_entry[0][key] += tree_data[key]
                    data_entry.append(tree_data)

            # all_networks_ds.data['spectral_networks'].append(data_entry)
            all_networks_ds.append(data_entry)

        # init_data = all_networks_ds.data['spectral_networks'][0][0]
        init_data = all_networks_ds[0][0]

    else:
        # all_networks_ds['spectral_networks'] is a 1-dim array,
        # of spectral network data.
        for sn in spectral_networks:
            skip_plotting = False
            for error in sn.errors:
                error_type, error_msg = error
                if error_type == 'Unknown':
                    skip_plotting = True
            if skip_plotting is True:
                continue

            sn_data = get_s_wall_plot_data(
                sn.s_walls, sw_data, logger_name, sn.phase,
            )
            # all_networks_ds.data['spectral_networks'].append(sn_data)
            all_networks_ds.append(sn_data)

        # init_data = all_networks_ds.data['spectral_networks'][0]
        init_data = all_networks_ds[0]

    # Initialization of the current plot data source.
    for key in list(current_ds.data.keys()):
        current_ds.data[key] = init_data[key]
        
    # prepare data sources for various objects to be plotted
    lines_ds = ColumnDataSource(
        data={k: current_ds.data[k] for k in 
              ['xs', 'ys', 'color', 'root', 'label'] 
              if k in list(current_ds.data.keys())
              }
    )
    arrows_ds = ColumnDataSource(
        data={k: current_ds.data[k] for k in 
              ['arrow_x', 'arrow_y', 'color', 'arrow_angle',
              'root', 'label'] 
              if k in list(current_ds.data.keys())
             }
    )

    # draw data points
    bokeh_figure.scatter(x='x', y='y', alpha=0.5, source=data_pts_ds,)
    
    # draw lines
    bokeh_figure.multi_line(
        xs='xs', ys='ys', color='color', line_width=1.5, 
        alpha='root', source=lines_ds,
    )

    # draw arrows
    bokeh_figure.triangle(
        x='arrow_x', y='arrow_y', color='color', alpha='root',
        angle='arrow_angle', size=8, source=arrows_ds,
    )

    # 4. Now start preparing the actual plot.

    bokeh_obj = {}
    notebook_vform_elements = []

    # XXX: Where is a good place to put the following?
    custom_js_code = ''
    if notebook is True or slide is True:
        with open('static/bokeh_callbacks.js', 'r') as fp:
            custom_js_code += fp.read()
            custom_js_code += '\n'

    # Data source for plot ranges
    if download is False and notebook is False and slide is False:
        range_callback = CustomJS(
            args={
                'x_range': bokeh_figure.x_range,
                'y_range': bokeh_figure.y_range
            },
            code=(custom_js_code + 'update_plot_range(x_range, y_range);'),
        )
        bokeh_figure.x_range.js_on_change('start', range_callback)
        bokeh_figure.y_range.js_on_change('start', range_callback)

    # XXX: Temporarily disabled this
    # TO DO: reinstate later, and remove the following line (it is just a patch)
    tree_idx_ds = ColumnDataSource()
    sn_idx_ds = ColumnDataSource()

    # # 'Redraw arrows' button.
    # redraw_arrows_button = Button(
    #     label='Redraw arrows',
    # )
    # redraw_arrows_button.js_on_click(
    #     CustomJS(
    #         args={
    #             'current_ds': current_ds,
    #             'x_range': bokeh_figure.x_range,
    #             'y_range': bokeh_figure.y_range
    #         },
    #         code=(custom_js_code + 'redraw_arrows(current_ds, x_range, y_range);'),
    #     )
    # )
    # bokeh_obj['redraw_arrows_button'] = redraw_arrows_button
    # notebook_vform_elements.append(redraw_arrows_button)

    # # 'Show data points' button
    # show_data_points_button = Button(
    #     label='Show data points',
    # )
    # show_data_points_button.js_on_event(
    #     ButtonClick,
    #     CustomJS(
    #         args={'current_ds': current_ds, 'data_pts_ds': data_pts_ds, 'hover': hover},
    #         code=(custom_js_code + 'show_data_points(current_ds, data_pts_ds, hover);'),
    #     )
    # )
    # bokeh_obj['show_data_points_button'] = show_data_points_button
    # notebook_vform_elements.append(show_data_points_button)

    # # 'Hide data points' button
    # hide_data_points_button = Button(
    #     label='Hide data points',
    # )
    # hide_data_points_button.js_on_event(
    #     ButtonClick,
    #     CustomJS(
    #         args={'current_ds': current_ds, 'data_pts_ds': data_pts_ds, 
    #           'hover': hover},
    #         code=(custom_js_code + 'hide_data_points(current_ds, data_pts_ds, 
    #           hover);'),
    #     )
    # )
    # bokeh_obj['hide_data_points_button'] = hide_data_points_button
    # notebook_vform_elements.append(hide_data_points_button)

    # # Prev/Next soliton tree button
    # tree_idx_ds = ColumnDataSource({'j': ['0']})
    # sn_idx_ds = ColumnDataSource({'i': ['0']})

    # if plot_two_way_streets is True:
    #     prev_soliton_tree_button = Button(
    #         label='<',
    #     )
    #     prev_soliton_tree_button.js_on_event(
    #         ButtonClick,
    #         CustomJS(
    #             args={
    #                 'current_ds': current_ds, 
    #                 'all_networks_ds': all_networks_ds, 
    #                 'sn_idx_ds': sn_idx_ds,
    #                 'tree_idx_ds': tree_idx_ds,
    #                 'plot_options_ds': plot_options_ds,
    #             },
    #             code=(
    #                 custom_js_code +
    #                 'show_prev_soliton_tree(current_ds, all_networks_ds, '+'
    #                 'sn_idx_ds, tree_idx_ds, '+
    #                 'plot_options_ds);'
    #             ),
    #         )
    #     )
    #     bokeh_obj['prev_soliton_tree_button'] = prev_soliton_tree_button
    #     notebook_vform_elements.append(prev_soliton_tree_button)

    #     next_soliton_tree_button = Button(
    #         label='>',
    #     )
    #     next_soliton_tree_button.js_on_event(
    #         ButtonClick,
    #         CustomJS(
    #             args={
    #                 'current_ds': current_ds, 'all_networks_ds': all_networks_ds, 'sn_idx_ds': sn_idx_ds,
    #                 'tree_idx_ds': tree_idx_ds,
    #                 'plot_options_ds': plot_options_ds,
    #             },
    #             code=(
    #                 custom_js_code +
    #                 'show_next_soliton_tree(current_ds, all_networks_ds, sn_idx_ds, tree_idx_ds, '
    #                 'plot_options_ds);'
    #             ),
    #         )
    #     )
    #     bokeh_obj['next_soliton_tree_button'] = next_soliton_tree_button
    #     notebook_vform_elements.append(next_soliton_tree_button)

    # Slider
    num_of_plots = len(all_networks_ds)
    if num_of_plots > 1:
        sn_slider = Slider(
            start=0, end=num_of_plots - 1,
            value=0, step=1, title="spectral network #"
        )

        sn_slider.js_on_change(
            'value',
            CustomJS(
                args={
                    'current_ds': current_ds, 
                    'all_networks_ds': all_networks_ds, 'sn_idx_ds': sn_idx_ds,
                    'data_pts_ds': data_pts_ds, 'phases_ds': phases_ds, 
                    'hover': hover,
                    'plot_options_ds': plot_options_ds, 
                    'tree_idx_ds': tree_idx_ds,
                    'lines_ds' : lines_ds, 'arrows_ds' : arrows_ds
                },
                code=(custom_js_code +
                    'sn_slider(' +
                    'cb_obj, ' +
                    'current_ds, ' +
                    'all_networks_ds, sn_idx_ds, data_pts_ds, phases_ds, '+
                    'hover, plot_options_ds, tree_idx_ds, lines_ds, arrows_ds)'
                ),
            )
        )
        plot = column(bokeh_figure, sn_slider)
        notebook_vform_elements = (
            [bokeh_figure, sn_slider] + notebook_vform_elements
        )
    else:
        plot = bokeh_figure
        notebook_vform_elements = (
            [bokeh_figure] + notebook_vform_elements
        )

    bokeh_obj['plot'] = plot
    
    # bokeh_figure.toolbar.active_scroll = plot.select_one(WheelZoomTool)
    # bokeh_figure.toolbar.active_scroll = 'auto'

    if notebook is True:
        # TODO: Include phase text input
        return column(*notebook_vform_elements)
    elif slide is True:
        return plot
    else:
        return bokeh.embed.components(bokeh_obj)


def get_s_wall_plot_data(s_walls, sw_data, logger_name, sn_phase):
    logger = logging.getLogger(logger_name)

    data_dict = {}
    data_dict['xs'] = []
    data_dict['ys'] = []
    data_dict['ranges'] = []
    data_dict['color'] = []
    data_dict['arrow_x'] = []
    data_dict['arrow_y'] = []
    data_dict['arrow_angle'] = []
    data_dict['label'] = []
    data_dict['root'] = []

    for s_wall in s_walls:
        z_segs = get_splits_with_overlap(s_wall.get_splits())
        for start, stop in z_segs:
            z_r = s_wall.z[start:stop].real
            z_i = s_wall.z[start:stop].imag
            a_i = int(numpy.floor(len(z_r) / 2.0))
            # TODO: Check if the arrow is within the plot range.
            a_angle = pi
            a_angle = (
                phase((z_r[a_i] - z_r[a_i - 1]) +
                      1j * (z_i[a_i] - z_i[a_i - 1]))
                - (pi / 2.0)
            )
            data_dict['xs'].append(z_r)
            data_dict['ys'].append(z_i)
            data_dict['ranges'].append(
                [z_r.min(), z_r.max(), z_i.min(), z_i.max()]
            )
            data_dict['arrow_x'].append(z_r[a_i])
            data_dict['arrow_y'].append(z_i[a_i])
            data_dict['arrow_angle'].append(a_angle)
        # XXX: temporary routine to label multiple roots.
        if s_wall.multiple_local_roots is not None:
            for roots in s_wall.multiple_local_roots:
                data_dict['label'].append(str(s_wall.label))
                root_label = ''
                for root in roots:
                    root_label += str(root.tolist()) + ', '
                data_dict['root'].append(root_label[:-2])
                color = sw_data.g_data.get_root_color(roots[0])
                if color is None:
                    color = '#000000'
                    logger.warning(
                        'Unknown root color for {} '
                        'of a spectral network with phase = {}.'
                        .format(s_wall.label, sn_phase)
                    )
                data_dict['color'].append(color)
        else:
            for root in s_wall.local_roots:
                data_dict['label'].append(str(s_wall.label))
                data_dict['root'].append(str(root.tolist()))
                color = sw_data.g_data.get_root_color(root)
                if color is None:
                    color = '#000000'
                    logger.warning(
                        'Unknown root color for {} '
                        'of a spectral network with phase = {}.'
                        .format(s_wall.label, sn_phase)
                    )
                data_dict['color'].append(color)

    return data_dict
