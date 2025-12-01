import os
from dagfactory import load_yaml_dags

YML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yml_definitions")

# Load DAGs from a folder, e.g., /path/to/dags
load_yaml_dags(globals_dict=globals(), dags_folder=YML_DIR)
