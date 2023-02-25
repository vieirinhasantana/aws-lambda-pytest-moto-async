import argparse
import logging

import toml


def format_parameter_overrides(parameters_overrides):
    template = lambda parameter, value: f'{parameter}="{value}"'
    parameters = [template(*item) for item in parameters_overrides.items()]
    return " ".join(parameters)


def format_parameters(parameters):
    p = parameters.copy()
    if "parameter_overrides" not in p:
        return p

    parameter_overrides = p.get("parameter_overrides")
    p["parameter_overrides"] = format_parameter_overrides(parameter_overrides)
    return p


def format_samconfig(parameters, version=0.1):
    base = {
        "version": version,
        "default": {"deploy": {"parameters": format_parameters(parameters)}},
    }
    return base


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate samconfig from config file")
    parser.add_argument("--account-id", type=str, required=True)
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--config-file", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--extra-parameter", action="append", default=[])

    args = parser.parse_args()
    region = args.region
    account_id = args.account_id

    extra_parameters = dict()
    for parameter in args.extra_parameter:
        parameter_split = parameter.split("=")
        if len(parameter_split) < 2:
            raise f"Missing value of key {parameter_split[0]}"

        extra_parameters.update({parameter_split[0]: parameter_split[1]})

    config = toml.load(args.config_file)
    version = config.get("version", 0.1)

    default_config = config.get("default", {})
    account_config = config.get(account_id, {})
    region_config = account_config.get(region, {})
    config_output = default_config.copy()
    config_output.update(region_config)
    config_output["region"] = region

    parameter_overrides = config_output.get("parameter_overrides", {}).copy()
    parameter_overrides.update(extra_parameters)

    if len(parameter_overrides) > 0:
        config_output["parameter_overrides"] = parameter_overrides

    samconfig = format_samconfig(config_output, version=version)

    with open(args.output, "w") as f:
        toml.dump(samconfig, f)

    logging.info("File samconfig generate was success.")
