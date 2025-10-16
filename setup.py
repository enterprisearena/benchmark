from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='enterprise_sandbox',
    version='0.1.0',
    description="EnterpriseArena: Multi-Platform Enterprise Software Benchmark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="EnterpriseArena Team",
    author_email="contact@enterprisearena.org",
    url="https://github.com/enterprisearena/benchmark",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    keywords="llm, benchmark, enterprise, software, evaluation, agents, multi-platform",
    project_urls={
        "Bug Reports": "https://github.com/enterprisearena/benchmark/issues",
        "Source": "https://github.com/enterprisearena/benchmark",
        "Documentation": "https://enterprisearena.readthedocs.io",
    },
)
