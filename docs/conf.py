import sys
import os

sys.path.append(os.path.abspath(".."))

project = "hw12"
copyright = "2024, Mariia"
author = "Mariia"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "nature"
html_static_path = ["_static"]
