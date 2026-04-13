"""Setup configuration for the automated-web-scraper package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="automated-web-scraper",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A production-ready automated web scraper supporting multiple libraries, scheduling, and flexible data export.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/automated-web-scraper",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/automated-web-scraper/issues",
        "Documentation": "https://github.com/yourusername/automated-web-scraper/docs",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "."},
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "webscraper=src.scraper:main",
        ],
    },
    include_package_data=True,
    package_data={
        "config": ["*.json", "*.yaml"],
    },
)
