import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airlogger",
    version="0.0.2",
    author="Guilherme Ferraz",
    author_email="guilherme@airfluencers.com",
    description="A package to organize logs in distributed systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/airfluencers/airlogger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
