from pathlib import Path
from typing import Any

import msgspec


def run(templates_dir: Path, lib_file: Path) -> None:
    lib = []

    for tpl in templates_dir.glob("*.json"):
        t = msgspec.json.decode(tpl.read_bytes())

        activity = get_first(t["spec"]["template"])
        if not activity:
            continue

        lib.append({
            "name": t["metadata"]["name"],
            "tags": t["spec"]["template"].get("tags", []),
            "type": activity["type"],
            "ref": tpl.stem,
            "purpose": t["spec"]["template"]["title"],
            "background": activity.get("background", False),
            "parameters": [
                {
                    "title": c["title"],
                    "type": c["type"],
                    "key": c["key"],
                    "required": c["required"],
                    "default": c.get("default")
                } for c in t["spec"]["schema"]["configuration"]
            ],
            "related": t.get("related")
        })

    lib_file.write_bytes(msgspec.json.encode(lib))


def get_first(experiment: dict[str, Any]) -> dict[str, Any]:
    if experiment.get("method"):
        return experiment["method"][0]

    if "steady-state-hypothesis" in experiment:
        return experiment["steady-state-hypothesis"]["probes"][0]

    if experiment.get("rollbacks"):
        return experiment["rollbacks"][0]
    
    return {}


if __name__ == "__main__":
    run(
        Path("./reliably_app/www/templates/experiments"),
        Path("./reliably_app/data/catalog.json"),
    )
