import yaml


def get_db_config(config_fname="config.yaml"):
    with open(config_fname) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config['DATABASE']


def get_apis(config_fname="config.yaml"):
    with open(config_fname) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return {'huggingface': config['HUGGINGFACE_API_TOKEN'], 'serpapi_key': config['SERPAPI_KEY']}