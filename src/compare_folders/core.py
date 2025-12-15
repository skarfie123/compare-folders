from datetime import datetime
from pathlib import Path

from rich import print  # pylint:disable=redefined-builtin
from rich.status import Status

NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def compare(
    source: Path,
    destination: Path,
    output_file: str,
    append: bool,
    verbose: bool,
):
    """
    Compares two folders and generates a report of the differences.
    """
    stats = {
        "Missing Folder": 0,
        "Missing File": 0,
        "Modified Newer": 0,
        "Modified Older": 0,
        "Extra Folder": 0,
        "Extra File": 0,
    }

    with open(output_file, "a" if append else "w", encoding="utf-8") as f:
        f.write(f"# compare-folders {NOW}\n\n")

        f.write(f"{source=}\n")
        f.write(f"{destination=}\n")

        f.write("\n## Missing\n\n")

        missing_dirs: set[Path] = set()
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

        extra_dirs: set[Path] = set()
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
    return stats
