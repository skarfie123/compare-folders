from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich import print  # pylint:disable=redefined-builtin
from rich.status import Status
from rich.table import Table

NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)


@cli.command()
def _main(
    source: Annotated[Path, typer.Argument(help="target file structure")],
    destination: Annotated[Path, typer.Argument(help="current file structure")],
    output_file: Annotated[str, typer.Option("-o", "--output")] = f"compare-folders_{NOW}.md",
    append: Annotated[
        bool, typer.Option(help="whether to append to output file if it already exists")
    ] = True,
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
):
    if not source.exists() or not source.is_dir():
        typer.echo(f"Source directory does not exist or is not a directory: {source}")
        raise typer.Exit(1)
    if not destination.exists() or not destination.is_dir():
        typer.echo(f"Destination directory does not exist or is not a directory: {destination}")
        raise typer.Exit(1)

    stats = {
        "Missing Folder": 0,
        "Missing File": 0,
        "Modified Newer": 0,
        "Modified Older": 0,
        "Extra Folder": 0,
        "Extra File": 0,
    }

    if not output_file:
        typer.echo("Output filename cannot be empty")
        raise typer.Exit(1)

    with open(output_file, "a" if append else "w", encoding="utf-8") as f:
        f.write(f"# compare-folders {NOW}\n\n")

        f.write(f"{source=}\n")
        f.write(f"{destination=}\n")

        f.write("\n## Missing\n\n")

        missing_dirs = set()
        with Status("Checking for missing files and folders...") as status:
            for path_in_source in source.rglob("*"):
                relative_path = path_in_source.relative_to(source)
                status.update(f"Checking missing: {relative_path}")
                if verbose:
                    print(f"Checking missing: {relative_path}")

                if any(relative_path.is_relative_to(p) for p in missing_dirs):
                    continue

                path_in_dest = destination / relative_path

                if not path_in_dest.exists():
                    if path_in_source.is_dir():
                        f.write(f"Missing Folder: {path_in_dest}\n")
                        stats["Missing Folder"] += 1
                        missing_dirs.add(relative_path)
                    else:
                        f.write(f"Missing File: {path_in_dest}\n")
                        stats["Missing File"] += 1

        f.write("\n## Modified\n\n")

        with Status("Checking for modified files...") as status:
            for path_in_source in source.rglob("*"):
                # We only care about files for modification check
                if not path_in_source.is_file():
                    continue

                relative_path = path_in_source.relative_to(source)
                status.update(f"Checking modified: {relative_path}")
                if verbose:
                    print(f"Checking modified: {relative_path}")

                # Skip if parent directory was missing
                if any(relative_path.is_relative_to(p) for p in missing_dirs):
                    continue

                path_in_dest = destination / relative_path
                if path_in_dest.is_file():
                    source_mtime = path_in_source.stat().st_mtime
                    dest_mtime = path_in_dest.stat().st_mtime
                    if source_mtime > dest_mtime:
                        f.write(f"Modified Newer: {path_in_source}\n")
                        stats["Modified Newer"] += 1
                    elif source_mtime < dest_mtime:
                        f.write(f"Modified Older: {path_in_source}\n")
                        stats["Modified Older"] += 1

        f.write("\n## Extra\n\n")

        extra_dirs = set()
        with Status("Checking for extra files and folders...") as status:
            for path_in_dest in destination.rglob("*"):
                relative_path = path_in_dest.relative_to(destination)
                status.update(f"Checking extra: {relative_path}")
                if verbose:
                    print(f"Checking extra: {path_in_dest}")

                if any(relative_path.is_relative_to(p) for p in extra_dirs):
                    continue

                path_in_source = source / relative_path

                if not path_in_source.exists():
                    if path_in_dest.is_dir():
                        f.write(f"Extra Folder: {path_in_dest}\n")
                        stats["Extra Folder"] += 1
                        extra_dirs.add(relative_path)
                    else:
                        f.write(f"Extra File: {path_in_dest}\n")
                        stats["Extra File"] += 1

    table = Table(title="Stats")
    table.add_column("Stat", justify="right", style="cyan")
    table.add_column("Count", style="magenta")
    for k, v in stats.items():
        table.add_row(k, str(v))
    print(table)

    print(f"\nWrote to file: {output_file}")


if __name__ == "__main__":
    cli()
