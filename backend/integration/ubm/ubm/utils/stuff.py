import yaml


def load_yaml(input_file):
    """
    Wrapper to load YAML

    Parameters
    ----------
    input_file: str
        Path of the input file

    Returns
    -------
    content: dict
        Content of the YAML file

    """
    with open(input_file) as f:
        return yaml.safe_load(f)
