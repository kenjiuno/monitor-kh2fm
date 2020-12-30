import os
import yaml
from typing import Dict

import export_tools
baseDir = os.path.dirname(export_tools.__file__)


def listFullPathFiles(dir, suffix):
    suffix = suffix.lower()
    for name in os.listdir(dir):
        if name.lower().endswith(suffix):
            yield os.path.join(dir, name)


def load() -> Dict:
    entire = {}
    for file in listFullPathFiles(os.path.join(baseDir, "instrs"), ".yml"):
        with open(file, "rt") as f:
            root = yaml.safe_load(f)
            entire.update(root)
    return entire
