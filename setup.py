from setuptools import setup, find_packages

setup(
    name="twitter-x-post-cleaner",
    version="0.1.0",
    description="A tool to automatically delete tweets, retweets, and replies from Twitter/X",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/twitter-x-post-cleaner",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    keywords="twitter, x, delete, clean, automation, selenium",
)
