from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt', 'r') as req_file:
        return req_file.read().splitlines()

setup(
    name="core",
    version="0.9",
    packages=find_packages(exclude=["tests*"]),
    install_requires=read_requirements(),
)
