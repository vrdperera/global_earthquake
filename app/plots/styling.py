"""Consistent visual styling for Bokeh figures."""

from __future__ import annotations


def style_plot(plot, *, show_grid: bool = True) -> None:
    """Apply the dashboard's restrained card-like plot treatment."""

    plot.background_fill_color = "#ffffff"
    plot.border_fill_color = "#ffffff"
    plot.outline_line_color = "#e4eaf2"
    plot.outline_line_width = 1
    plot.min_border_left = 58
    plot.min_border_right = 24
    plot.min_border_top = 58
    plot.min_border_bottom = 50
    plot.title.text_color = "#172b4d"
    plot.title.text_font = "Inter"
    plot.title.text_font_size = "15px"
    plot.title.text_font_style = "bold"
    plot.title.offset = 8
    plot.axis.axis_label_text_color = "#64748b"
    plot.axis.axis_label_text_font = "Inter"
    plot.axis.axis_label_text_font_size = "11px"
    plot.axis.major_label_text_color = "#64748b"
    plot.axis.major_label_text_font = "Inter"
    plot.axis.major_label_text_font_size = "10px"
    plot.axis.axis_line_color = "#d9e1ec"
    plot.axis.major_tick_line_color = "#d9e1ec"
    plot.axis.minor_tick_line_color = None
    plot.grid.grid_line_color = "#edf1f6" if show_grid else None
    plot.grid.grid_line_alpha = 0.9
    plot.toolbar.logo = None
    plot.styles = {
        "border-radius": "16px",
        "box-shadow": "0 7px 22px rgba(30, 50, 85, 0.07)",
        "overflow": "hidden",
    }
