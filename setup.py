from setuptools import setup, find_packages

setup(
    name="tttj-scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright==1.54.0",
        "pydantic==2.11.7",
        "typer==0.16.1",
        "rich==14.1.0",
        "pandas==2.3.2",
    ],
    python_requires=">=3.8",
)

