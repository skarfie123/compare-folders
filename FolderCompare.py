import os
from pathlib import Path
from datetime import datetime
import argparse


def main(args):

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f"FolderCompare_{now}.md", "a") as f:
        f.write(f"# Folder Compare {now}\n\n")

        f.write(f"{args.source=}\n")
        f.write(f"{args.destination=}\n")

        f.write(f"\n## Missing\n\n")

        missingDirs = set()
        for dirname, dirs, files in os.walk(args.source):
            if dirname in missingDirs:
                continue
            for filename in files + dirs:
                path1 = os.path.join(dirname, filename)
                path2 = path1.replace(args.source, args.destination)
                if not os.path.exists(path2):
                    f.write(f"Missing {path2}\n")
                    if Path(path1).is_dir():
                        missingDirs.add(path1)

        f.write(f"\n## Modified\n\n")

        for dirname, dirs, files in os.walk(args.source):
            if dirname in missingDirs:
                continue
            for filename in files:
                path1 = os.path.join(dirname, filename)
                path2 = path1.replace(args.source, args.destination)
                if not os.path.exists(path2):
                    pass
                elif Path(path1).stat().st_mtime > Path(path2).stat().st_mtime:
                    f.write(f"Newer {path1}\n")
                elif Path(path1).stat().st_mtime < Path(path2).stat().st_mtime:
                    f.write(f"Older {path1}\n")

        f.write(f"\n## Extra\n\n")

        extraDirs = set()
        for dirname, dirs, files in os.walk(args.destination):
            if dirname in extraDirs:
                continue
            for filename in files + dirs:
                path2 = os.path.join(dirname, filename)
                path1 = path2.replace(args.destination, args.source)
                if not os.path.exists(path1):
                    f.write(f"Extra {path2}\n")
                    if Path(path2).is_dir():
                        extraDirs.add(path2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("FolderCompare")
    parser.add_argument("source", help="target file structure")
    parser.add_argument("destination", help="current file structure")
    main(parser.parse_args())