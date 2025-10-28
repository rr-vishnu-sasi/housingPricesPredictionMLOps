"""
Setup script for the Housing Price Prediction MLOps project.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="housing-price-prediction-mlops",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An end-to-end MLOps project for housing price prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/housing-price-prediction",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "pyyaml>=6.0",
        "joblib>=1.3.0",
        "jupyter>=1.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "mlops": [
            "mlflow>=2.8.0",
            "dvc>=3.0.0",
            "great-expectations>=0.17.0",
            "evidently>=0.4.0",
        ],
        "serving": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.4.0",
        ],
    },
)
