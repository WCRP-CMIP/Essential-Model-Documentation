from setuptools import setup, find_packages

setup(
    name='mkdocs-html-search-plugin',
    version='0.1.0',
    description='MkDocs plugin to index HTML files in search',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.0',
        'beautifulsoup4>=4.9.0',
    ],
    entry_points={
        'mkdocs.plugins': [
            'html_search = html_search:HTMLSearchPlugin',
        ]
    },
    python_requires='>=3.6',
)
