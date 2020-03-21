// function show_data_points(current_ds, data_pts_ds, hover) {
//     var cd = current_ds.data;
//     var dpd = data_pts_ds.data;
//     dpd['x'] = [];
//     dpd['y'] = [];

//     for (var i = 0, i_stop = cd['xs'].length; i < i_stop; i++) {
//         dpd['x'] = dpd['x'].concat(cd['xs'][i]);
//         dpd['y'] = dpd['y'].concat(cd['ys'][i]);
//     }
//     hover.attributes.tooltips = null;
//     // data_pts_ds.trigger('change');
//     data_pts_ds.change.emit();
// }

function show_data_points(plot_data_pts_ds, data_pts_ds, hover_tool) {
    for (var key in plot_data_pts_ds.data) {
        plot_data_pts_ds.data[key] = data_pts_ds.data[key]
    }

    // hover_tool.attributes.tooltips = null;
    plot_data_pts_ds.change.emit();
}

function hide_data_points(plot_data_pts_ds, data_pts_ds, hover_tool) {
    for (var key in plot_data_pts_ds.data) {
        plot_data_pts_ds.data[key] = []
    }

    // hover_tool.attributes.tooltips = [['name', '@label'], ['root', '@root']];
    plot_data_pts_ds.change.emit();
}

// function sn_slider(cb_obj, current_ds, 
//     all_networks_ds, sn_idx_ds, data_pts_ds, phases_ds, hover,
//     plot_options_ds, tree_idx_ds) 
// {
//     // var cd = current_ds['data'];
//     // var snd = all_networks_ds['data'];
//     // var dpd = data_pts_ds['data'];
//     // var pd = phases_ds['data'];
//     // var current_sn_idx = sn_idx_ds['data'];
//     var sn_idx = cb_obj.value;
//     // var plot_options = plot_options_ds['data'];
//     var notebook = plot_options_ds.data['notebook'];
//     var show_trees = plot_options_ds['show_trees'];
//     // var show_trees = 'false'
//     // var tree_idx = tree_idx_ds['data'];
    
//     sn_idx_ds.data['i'] = sn_idx;
//     // tree_idx['j'] = 0;
//     // if (show_trees == 'true') {
//     //     document.getElementById("current_tree_idx").innerHTML = 'All';
//     // }

//     for (var key in current_ds.data) {
//         if (current_ds.data.hasOwnProperty(key)) {
//             if (show_trees == 'false') {
//                 current_ds.data[key] = all_networks_ds.data['spectral_networks'][sn_idx][key];
//             } else {
//                 current_ds.data[key] = all_networks_ds.data['spectral_networks'][sn_idx][0][key];
//             }
//         }
//     }

//     // current_ds.trigger('change');
//     current_ds.change.emit()
//     // sn_idx_ds.trigger('change');
//     sn_idx_ds.change.emit()
//     // tree_idx_ds.trigger('change');
//     // tree_idx_ds.change.emit()
//     hide_data_points(current_ds, data_pts_ds, hover);
//     if (notebook == 'false') {
//         document.getElementById("phase").innerHTML = pd['phase'][sn_idx];
//     }

//     ///////

//     // current_sn_idx['i'] = sn_idx;
//     // for (var key in cd) {
//     //     if (cd.hasOwnProperty(key)) {
//     //         cd[key] = snd['spectral_networks'][sn_idx][0][key];
//     //     }
//     // }
//     // current_ds.trigger('change');
//     // sn_idx_ds.trigger('change');
//     // // hide_data_points(current_ds, data_pts_ds, hover);
//     // // if (notebook == 'false') {
//     // //     document.getElementById("phase").innerHTML = pd['phase'][sn_idx];
//     // // }
// }

function sn_slider(cb_obj, //
    all_networks_ds, sn_idx_ds, data_pts_ds, plot_data_pts_ds, //
    all_data_pts_ds, phases_ds, hover_tool, //
    plot_options_ds, tree_idx_ds, lines_ds, arrows_ds) {

    // Declare some local variables
    var sn_idx = cb_obj.value;  // slider's current value
    var show_trees = plot_options_ds.data['show_trees'];
    var notebook = plot_options_ds.data['notebook'];

    // change the index of the current spectral network
    sn_idx_ds.data['i'] = sn_idx;

    // update the ColumnDataSource containing current lines data
    for (var key in lines_ds.data) {
        if (all_networks_ds[sn_idx].hasOwnProperty(key)) {
            if (show_trees == 'false') {
                lines_ds.data[key] = all_networks_ds[sn_idx][key];
            } else {
                lines_ds.data[key] = all_networks_ds[sn_idx][0][key];
            }
        }
    }

    // update the ColumnDataSource containing current arrows data
    for (var key in arrows_ds.data ) {
        if (all_networks_ds[sn_idx].hasOwnProperty(key)) {
            if (show_trees == 'false') {
                arrows_ds.data[key] = all_networks_ds[sn_idx][key];
            } else {
                arrows_ds.data[key] = all_networks_ds[sn_idx][0][key];
            }
        }
    }

    // Update the ColumnDataSource of the data points
    for (var key in data_pts_ds.data ) {
        data_pts_ds.data[key] = all_data_pts_ds.data[key][sn_idx]
    }

    // Update the ColumnDataSource of the plotted data points, if they are shown
    for (var key in plot_data_pts_ds.data ) {
        if (plot_data_pts_ds.data[key].length > 0) {
            plot_data_pts_ds.data[key] = all_data_pts_ds.data[key][sn_idx]
        }
    }

    // push changes to outside data given as argument to this function
    sn_idx_ds.change.emit()
    arrows_ds.change.emit()
    lines_ds.change.emit()
    data_pts_ds.change.emit()
    plot_data_pts_ds.change.emit()

    hide_data_points(data_pts_ds, hover_tool);
    if (notebook == 'false') {
        document.getElementById("phase").innerHTML = pd['phase'][sn_idx];
    }
}


function change_soliton_tree(
    current_ds, all_networks_ds, sn_idx_ds, tree_idx_ds, plot_options_ds, change
) {
    var cd = current_ds.data;
    var snd = all_networks_ds.data;
    var sn_idx = sn_idx_ds.data;
    var tree_idx = tree_idx_ds.data;
    var plot_options = plot_options_ds.data;
    var notebook = plot_options['notebook'];
    var show_trees = plot_options['show_trees'];

    var sn_i = sn_idx['i'];
    var tree_j = Number(tree_idx['j']) + change;
    var max_tree_j = snd['spectral_networks'][sn_i].length;
    if (tree_j > max_tree_j) {
        tree_j = max_tree_j;
    } else if (tree_j < 0) {
        tree_j = 0;
    }
    
    for (var key in cd) {
        if (cd.hasOwnProperty(key)) {
            cd[key] = snd['spectral_networks'][sn_i][tree_j][key];
        }
    }

    if (notebook == 'false') {
        var tree_idx_label = document.getElementById("current_tree_idx");
        if (tree_j == 0) {
            tree_idx_label.innerHTML = 'All';
        } else {
            tree_idx_label.innerHTML = tree_j - 1;
        }
    }
    
    current_ds.trigger('change');
    tree_idx['j'] = String(tree_j);
    tree_idx_ds.trigger('change');
}

function show_prev_soliton_tree(
    current_ds, all_networks_ds, sn_idx_ds, tree_idx_ds, plot_options_ds
) {
    change_soliton_tree(
        current_ds, all_networks_ds, sn_idx_ds, tree_idx_ds, plot_options_ds, -1
    );
}

function show_next_soliton_tree(
    current_ds, all_networks_ds, sn_idx_ds, tree_idx_ds, plot_options_ds
) {
    change_soliton_tree(
        current_ds, all_networks_ds, sn_idx_ds, tree_idx_ds, plot_options_ds, 1
    );   
}

function redraw_arrows(current_ds, x_range, y_range) {
    var cd = current_ds.data;
    var x_s = x_range.get('start');
    var x_e = x_range.get('end');
    var y_s = y_range.get('start');
    var y_e = y_range.get('end');

    for (var i = 0, i_stop = cd['arrow_x'].length; i < i_stop; i++) {
        // Domain of the segment.
        var range = cd['ranges'][i];
        var x_min = range[0];
        var x_max = range[1];
        var y_min = range[2];
        var y_max = range[3];

        if ((x_max < x_s) || (x_min > x_e) || (y_max < y_s) || (y_min > y_e)) {
            // The segment is out of screen.
            continue;
        }

        // Now find the new location for the arrow.
        var a_x;
        var a_y;
        var a_i;
        var x = cd['xs'][i];
        var y = cd['ys'][i];
        var x_length = x.length;
        var denom = 2;
        var found = false;

        while ((Math.floor(x_length / denom) > 0) && !found) {
            for (var j = 1; j < denom; j += 2) {
                a_i = Math.floor(x_length * j / denom);
                a_x = x[a_i];
                a_y = y[a_i];
                if ((a_x >= x_s) && (a_x <= x_e) && 
                    (a_y >= y_s) && (a_y <= y_e)) {
                    found = true;
                    break;
                }
            }
            denom *= 2;
        }
        cd['arrow_x'][i] = a_x;
        cd['arrow_y'][i] = a_y;
        var Dx = x[a_i] - x[a_i - 1];
        var Dy = y[a_i] - y[a_i - 1];
        cd['arrow_angle'][i] = Math.atan2(Dy, Dx) - (Math.PI / 2);
    }
    current_ds.trigger('change');
}

function update_plot_range(x_range, y_range) {
    var x_s = x_range.get('start');
    var x_e = x_range.get('end');
    var y_s = y_range.get('start');
    var y_e = y_range.get('end');

    var plot_range_input = document.getElementById("plot_range_input");
    plot_range_input.value =
        "[[" + x_s + "," + x_e + "],[" + y_s + "," + y_e + "]]";
}
