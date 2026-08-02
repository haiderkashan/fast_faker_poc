from setuptools import setup, find_packages

setup(
    name="async-batch-faker",
    version="0.1.0",
    author="Kashan Haider",
    description="A high-performance, asynchronous, vectorized mock data generator.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    
    # CRITICAL: This tells pip to include your .txt locale files!
    include_package_data=True,
    package_data={
        "async_batch_faker": ["data/*/*.txt", "data/*.txt"],
    },
    
    # These are the libraries someone needs to run your code
    install_requires=[
        "numpy>=1.20.0",
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)