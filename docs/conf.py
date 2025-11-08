#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import builtins

import sphinx_rtd_theme

sys.path.insert(0, "../usr/lib/python3/dist-packages/")

# Fix gettext syntax
builtins._ = lambda x:x

extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary']
autosummary_generate = True

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'linuxmuster-linuxclient7'
copyright = '2020, Dorian Zedler'
author = 'Dorian Zedler'

def setup(app):
    app.add_css_file("theme_overrides.css")

version = "unknown"
with open("../debian/changelog") as changelogFile:
    changelog = changelogFile.read()
    version = changelog.split("\n")[0].split("(")[1].split(")")[0]
    
release = version

language = 'en_GB'
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = False

html_theme = 'sphinx_rtd_theme'
html_logo = '_static/logo.png'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

htmlhelp_basename = 'linuxmuster-linuxclient7doc'

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'linuxmuster-7.tex', 'linuxmuster-linuxclient7 Documentation',
     'Dorian Zedler', 'manual'),
]

man_pages = [
    (master_doc, 'linuxmuster-linuxclient7', 'linuxmuster-linuxclient7 Documentation',
     [author], 1)
]


texinfo_documents = [
    (master_doc, 'linuxmuster-linuxclient7', 'linuxmuster-linuxclient7 Documentation',
     author, 'linuxmuster-linuxclient7', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
