"""DES040 balanced placements through the maintained local-unit generator."""

from trimmed_export import export as export_local_units


def export(config, output):
    if config.get("placement", {}).get("id") != "balanced":
        raise ValueError("Balanced exporter requires the named placement contract")
    if config["placement"]["global_services"] != "frozen-reference-inventory":
        raise ValueError("Global service inventory requires a separately reviewed model")
    return export_local_units(config, output)
