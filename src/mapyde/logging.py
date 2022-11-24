# https://stackoverflow.com/questions/71077706/redirect-print-and-or-logging-to-panel
from __future__ import annotations

import os
from typing import Any, Iterable

from rich.console import Console, ConsoleOptions
from rich.layout import Layout


class ConsolePanel(Console):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        console_file = open(os.devnull, "w")
        super().__init__(record=True, file=console_file, *args, **kwargs)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Iterable[str]:
        texts = self.export_text(clear=False).split("\n")
        if options.height:
            yield from texts[-options.height :]
        yield from texts


class Interface:
    def __init__(self) -> None:
        self.console: list[ConsolePanel] = [ConsolePanel() for _ in range(2)]

    def get_renderable(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(self.console[0], name="top"),
            Layout(self.console[1], name="bottom", size=10),
        )
        layout.children[0]
        return layout
