import asyncio
import random

import pandas as pd
from plotnine import aes, geom_point, ggplot, theme_light
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Streaming data"),
    ui.input_slider("rate", "Refresh rate", 0.2, 2, 0.2, step=0.05),
    ui.input_action_button("reset", "Reset", style="background: blue; color: white"),
    ui.output_plot("random_walk"),
)


def server(input, output, session):
    data = {'x': [1, 2], 'y': [10, 10]}
    data = pd.DataFrame(data)
    val = reactive.Value(data)

    @reactive.Effect
    @reactive.event(input.reset)
    def _():
        val.set(data)

    @reactive.Calc
    def random_data():
        reactive.invalidate_later(input.rate())

        # Create fake data
        with reactive.isolate():
            last_run = val.get()

        # Generate new row
        new_x = last_run['x'].iloc[-1] + 1
        new_y = last_run['y'].iloc[-1] + random.uniform(-5, 5)
        new_row = pd.DataFrame({'x': [new_x], 'y': [new_y]})

        # Append new row to DataFrame
        out = pd.concat([last_run, new_row], axis=0, ignore_index=True)
        out = out.tail(100)

        val.set(out)
        return out

    @output
    @render.plot
    async def random_walk():
        plot = (
            ggplot(
                random_data(),
                aes(
                    x="x",
                    y="y"
                ),
            )
            + geom_point()
            + theme_light()
        )
        return plot


app = App(app_ui, server)
