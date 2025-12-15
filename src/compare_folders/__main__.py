import os
from datetime import datetime
from typing import Annotated

import typer
from rich import print  # pylint:disable=redefined-builtin
from rich.status import Status
from rich.table import Table

NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)


@cli.command()
def _main(
    source: Annotated[str, typer.Argument(help="target file structure")],
    destination: Annotated[str, typer.Argument(help="current file structure")],
    output_file: Annotated[str, typer.Option("-o", "--output")] = f"compare-folders_{NOW}.md",
    append: Annotated[
        bool, typer.Option(help="whether to append to output file if it already exists")
    ] = True,
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
):
    if not os.path.exists(source):
        typer.echo(f"source directory does not exist: {source}")
        raise typer.Exit(1)
    if not os.path.exists(destination):
        typer.echo(f"destination directory does not exist: {destination}")
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
        typer.echo("output filename cannot be empty")
        raise typer.Exit(1)

    with open(output_file, "a" if append else "w", encoding="utf-8") as f:
        f.write(f"# compare-folders {NOW}\n\n")

        f.write(f"{source=}\n")
        f.write(f"{destination=}\n")

        f.write("\n## Missing\n\n")

        missing_dirs = set()
        with Status("Checking missing files") as status:
            for dirname, dirs, files in os.walk(source):
                status.update(f"Checking directory for missing: {dirname}")
                if verbose:
                    print("Checking directory for missing:", dirname)
                should_continue = False
                for d in missing_dirs:
                    if dirname.startswith(d):
                        should_continue = True
                        break
                if should_continue:
                    continue
                for filename in files:
                    path1 = os.path.join(dirname, filename)
                    path2 = path1.replace(source, destination)
                    if not os.path.exists(path2):
                        f.write(f"Missing File {path2}\n")
                        stats["Missing File"] += 1
                for filename in dirs:
                    path1 = os.path.join(dirname, filename)
                    path2 = path1.replace(source, destination)
                    if not os.path.exists(path2):
                        f.write(f"Missing Folder {path2}\n")
                        stats["Missing Folder"] += 1
                        missing_dirs.add(path1)

        f.write("\n## Modified\n\n")

        with Status("Checking modified files") as status:
            for dirname, dirs, files in os.walk(source):
                status.update(f"Checking directory for modified: {dirname}")
                if verbose:
                    print("Checking directory for modified:", dirname)
                should_continue = False
                for d in missing_dirs:
                    if dirname.startswith(d):
                        should_continue = True
                        break
                if should_continue:
                    continue
                for filename in files:
                    path1 = os.path.join(dirname, filename)
                    path2 = path1.replace(source, destination)
                    if not os.path.exists(path2):
                        pass
                    elif os.stat(path1).st_mtime > os.stat(path2).st_mtime:
                        f.write(f"Modified Newer {path1}\n")
                        stats["Modified Newer"] += 1
                    elif os.stat(path1).st_mtime < os.stat(path2).st_mtime:
                        f.write(f"Modified Older {path1}\n")
                        stats["Modified Older"] += 1

        f.write("\n## Extra\n\n")

        extra_dirs = set()
        with Status("Checking extra files") as status:
            for dirname, dirs, files in os.walk(destination):
                status.update(f"Checking directory for extras: {dirname}")
                if verbose:
                    print("Checking directory for extras:", dirname)
                should_continue = False
                for d in extra_dirs:
                    if dirname.startswith(d):
                        should_continue = True
                        break
                if should_continue:
                    continue
                for filename in files:
                    path2 = os.path.join(dirname, filename)
                    path1 = path2.replace(destination, source)
                    if not os.path.exists(path1):
                        f.write(f"Extra File {path2}\n")
                        stats["Extra File"] += 1
                for filename in dirs:
                    path2 = os.path.join(dirname, filename)
                    path1 = path2.replace(destination, source)
                    if not os.path.exists(path1):
                        f.write(f"Extra Folder {path2}\n")
                        stats["Extra Folder"] += 1
                        extra_dirs.add(path2)

    table = Table(title="Stats")
    table.add_column("Stat", justify="right", style="cyan")
    table.add_column("Count", style="magenta")
    for k, v in stats.items():
        table.add_row(k, str(v))
    print(table)

    print("\nWrote to file:", output_file)


if __name__ == "__main__":
    cli()
