from setuptools import setup

setup(
    name="mkdocs-nav-generator",
    version="0.1.0",
    py_modules=["nav_generator"],
    package_dir={"": "."},
    entry_points={
        "mkdocs.plugins": [
            "nav-generator = nav_generator:NavGeneratorPlugin",
        ]
    },
)
