import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = [
        line.strip() for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]

setuptools.setup(
    name="loc2elr",                    
    version="0.4.2",                                                      
    author="Katherine Whitelock",
    author_email="ktwhitelock@outlook.com",
    description="An algorithm which uses BPLAN geography and NWR Track Models to derive unique standard track granular buckets for STANOX codes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/katielocks/loc2elr",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
)

