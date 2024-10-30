#!/usr/bin/env python
"""
This script will parse and relabel the Applet elements in each plasma config
file it finds on each folder.
"""

from pathlib import Path
from collections import Counter

import re


def parse_file(file: Path):
    lines = file.read_text().splitlines()

    pattern = r"\[Containments\]\[(\d+)\]\[Applets\]\[(\d+)\](.*)"

    counts = Counter()
    id_map = dict()

    for i, line in enumerate(lines):
        result = re.match(pattern, line)
        if result:
            print(f"Found: {line}")

            cont_id, app_id, rmnd = result.groups()
            cont_id = int(cont_id)
            app_id = int(app_id)

            if app_id not in id_map:
                counts[cont_id] += 1
                id_map[app_id] = cont_id + counts[cont_id]
                print(f"Changing {app_id} to {id_map[app_id]}")

            lines[i] = f"[Containments][{cont_id}][Applets][{id_map[app_id]}]{rmnd}"

    # second pass to fix references to the applet ids in AppletOrder
    for i, line in enumerate(lines):
        if line.startswith("AppletOrder"):
            _, id_list = line.split("=")
            applet_ids = id_list.strip().split(";")
            applet_ids = [str(id_map[int(id)]) for id in applet_ids]
            lines[i] = f"AppletOrder={';'.join(applet_ids)}"

    file.write_text("\n".join(lines))


def main():
    for file in Path(".").rglob("plasma-org.kde.plasma.desktop-appletsrc"):
        print(f"Parsing {file}")
        parse_file(file)


if __name__ == "__main__":
    main()
