from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="yd_extractor",
    version="0.1.0",
    description="A package for extracting data for Year in Data project",
    author="Aebel Shajan",
    author_email="aebel.projects@gmail.com",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
