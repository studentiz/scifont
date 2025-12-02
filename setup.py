from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scifont",
    version="0.1.3",
    author="studentiz",
    author_email="studentiz@live.com",
    description="Force publication-quality, editable fonts in Matplotlib figures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/studentiz/scifont",
    packages=find_packages(),
    # CRITICAL: This ensures the 'fonts' folder is included in the wheel
    include_package_data=True,
    package_data={
        "scifont": ["fonts/*.ttf"],
    },
    install_requires=[
        "matplotlib>=3.3.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",
)