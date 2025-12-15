from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print  # pylint:disable=redefined-builtin
from rich.table import Table

from .core import NOW, compare
from .gui import App

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)


@cli.command()
def _main(
    source: Annotated[Optional[Path], typer.Argument(help="target file structure")] = None,
    destination: Annotated[Optional[Path], typer.Argument(help="current file structure")] = None,
    output_file: Annotated[str, typer.Option("-o", "--output")] = f"compare-folders_{NOW}.md",
    append: Annotated[
        bool, typer.Option(help="whether to append to output file if it already exists")
    ] = True,
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
    gui: Annotated[bool, typer.Option("--gui", help="Launch the GUI")] = False,
):
    if gui:
        app = App(
            source=str(source) if source else "",
            destination=str(destination) if destination else "",
            output_file=output_file,
        )
        app.mainloop()
        return

    if not source or not destination:
        typer.echo("Source and destination are required in non-GUI mode.")
        raise typer.Exit(1)

    if not source.exists() or not source.is_dir():
        typer.echo(f"Source directory does not exist or is not a directory: {source}")
        raise typer.Exit(1)
    if not destination.exists() or not destination.is_dir():
        typer.echo(f"Destination directory does not exist or is not a directory: {destination}")
        raise typer.Exit(1)

    if not output_file:
        typer.echo("Output filename cannot be empty")
        raise typer.Exit(1)

    stats = compare(source, destination, output_file, append, verbose)

    table = Table(title="Stats")
    table.add_column("Stat", justify="right", style="cyan")
    table.add_column("Count", style="magenta")
    for k, v in stats.items():
        table.add_row(k, str(v))
    print(table)

    print(f"\nWrote to file: {output_file}")


if __name__ == "__main__":
    cli()
