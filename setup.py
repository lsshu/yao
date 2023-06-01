from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yao",
    version="0.0.6",
    description="Dev",
    python_requires=">=3.9",
    author="Lsshu",
    author_email="admin@lsshu.cn",
    url="https://github.com/lsshu/yao",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[
        "fastapi[all]",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "SQLAlchemy==1.4.46",
        "Pillow",
        "pymysql",
        "sqlalchemy-mptt",
        "user-agents",
        "requests",
        "openpyxl",
        "aioredis",
        "filetype",
        "pycryptodome",
    ]
)
