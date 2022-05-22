import argparse
import codecs
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main(args):
    stats = defaultdict(lambda: 0)

    with codecs.open(
        args.output_file if args.output_file else "NUL", "a", "utf-8"
    ) as f:
        f.write(f"# Folder Compare {NOW}\n\n")

        f.write(f"{args.source=}\n")
        f.write(f"{args.destination=}\n")

        f.write("\n## Missing\n\n")

        missingDirs = set()
        for dirname, dirs, files in os.walk(args.source):
            print("Checking directory for missing:", dirname)
            shouldContinue = False
            for d in missingDirs:
                if d in dirname:
                    shouldContinue = True
                    break
            if shouldContinue:
                continue
            for filename in files + dirs:
                path1 = os.path.join(dirname, filename)
                path2 = path1.replace(args.source, args.destination)
                if not os.path.exists(path2):
                    if Path(path1).is_dir():
                        f.write(f"Missing Folder {path2}\n")
                        stats["Missing Folder"] += 1
                        missingDirs.add(path1)
                    else:
                        f.write(f"Missing File {path2}\n")
                        stats["Missing File"] += 1

        f.write("\n## Modified\n\n")

        for dirname, dirs, files in os.walk(args.source):
            print("Checking directory for modified:", dirname)
            shouldContinue = False
            for d in missingDirs:
                if d in dirname:
                    shouldContinue = True
                    break
            if shouldContinue:
                continue
            for filename in files:
                path1 = os.path.join(dirname, filename)
                path2 = path1.replace(args.source, args.destination)
                if not os.path.exists(path2):
                    pass
                elif Path(path1).stat().st_mtime > Path(path2).stat().st_mtime:
                    f.write(f"Modified Newer {path1}\n")
                    stats["Modified Newer"] += 1
                elif Path(path1).stat().st_mtime < Path(path2).stat().st_mtime:
                    f.write(f"Modified Older {path1}\n")
                    stats["Modified Older"] += 1

        f.write("\n## Extra\n\n")

        extraDirs = set()
        for dirname, dirs, files in os.walk(args.destination):
            print("Checking directory for extras:", dirname)
            shouldContinue = False
            for d in extraDirs:
                if d in dirname:
                    shouldContinue = True
                    break
            if shouldContinue:
                continue
            for filename in files + dirs:
                path2 = os.path.join(dirname, filename)
                path1 = path2.replace(args.destination, args.source)
                if not os.path.exists(path1):
                    if Path(path2).is_dir():
                        f.write(f"Extra Folder {path2}\n")
                        stats["Extra Folder"] += 1
                        extraDirs.add(path2)
                    else:
                        f.write(f"Extra File {path2}\n")
                        stats["Extra File"] += 1

    if stats:
        print("\nstat\t\tcount\n" + "-" * 20)
        for k, v in stats.items():
            print(f"{k}\t{v}")

    if args.output_file:
        print("\nWrote to file:", args.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("FolderCompare")
    parser.add_argument("source", help="target file structure")
    parser.add_argument("destination", help="current file structure")
    parser.add_argument(
        "-o",
        "--output-file",
        help="output file",
        const=f"FolderCompare_{NOW}.md",
        nargs="?",
    )
    main(parser.parse_args())
