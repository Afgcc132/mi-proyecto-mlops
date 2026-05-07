from setuptools import setup, find_packages
from typing import List
import os



def get_requirements() -> List[str]:

    requirement_lst: List[str] = []
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                requirement = line.strip()
                # La línea '-e .' en requirements.txt sirve para instalar el paquete actual
                # en modo editable, por lo que no debe incluirse en la lista de dependencias.
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found. Please make sure it exists in the same directory as setup.py.")

    return requirement_lst
setup(
    name="mlops_project",
    version="0.1.0",
    packages=find_packages(),
    install_requires=get_requirements(),        
)