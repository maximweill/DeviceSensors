from shiny.express import input, ui
from shiny import reactive
from shinywidgets import render_plotly
import plotly.express as px
from get_data import devices_data,numeric_cols,manufacturers
from functools import partial
from shiny.ui import page_navbar

@reactive.calc
def filtered_data():
    sub = devices_data[devices_data["manufacturer"] == input.manufacturer()]
    model_text = input.model_text().strip()
    if model_text:
        sub = sub[sub["model"].str.contains(model_text, case=False, na=False)]
    return sub

ui.page_opts(
    title="Device Sensors", 
    page_fn=partial(page_navbar, id="page"),  
)

with ui.nav_panel("Filters"):
    with ui.layout_columns():
        with ui.card(title="Filters", full_screen=False):
            ui.input_select("manufacturer", "Manufacturer", choices=manufacturers, selected="Apple")
            ui.input_text("model_text", "Text contained in Model Name", value="")
            ui.input_select("variable", "Variable", choices=numeric_cols, selected="accelerometer_rate")
        with ui.card(title="Distribution", full_screen=False):
            @render_plotly
            def boxplot():
                sub = filtered_data()
                var = input.variable()
                if not sub.empty and var in sub:
                    fig = px.box(
                        sub,
                        y=var
                    ).update_layout(title="Distribution")
                    return fig

with ui.nav_panel("Plot"):  
    with ui.card(title="Histogram", full_screen=True):
        @render_plotly
        def histogram():
            sub = filtered_data()
            var = input.variable()
            ordered = sub.sort_values(var)
            fig = px.bar(
                ordered,
                x="model",
                y=var
            ).update_layout(
                title="Ordered Histogram by Model",
                xaxis_title="Model",
                yaxis_title=var
            )
            return fig


with ui.nav_panel("About"):  
    ui.markdown(
        """
        **About this site**

        Data comes from [phyphox sensordb](https://phyphox.org/sensordb).

        _This website was made by Maxim Weill._
        """
    )







