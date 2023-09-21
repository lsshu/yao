from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yao",
    version="0.1.3",
    description="Dev",
    python_requires=">=3.8",
    author="Lsshu",
    author_email="admin@lsshu.cn",
    url="https://github.com/lsshu/yao",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[
        "fastapi[all]==0.83.0",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]",
        "SQLAlchemy==1.4.46",
        "Pillow",
        "PyMySQL==1.0.2",
        "sqlalchemy-mptt==0.2.5",
        "user-agents==2.2.0",
        "requests",
        "openpyxl",
        "aioredis",
        "filetype==1.2.0",
        "pycryptodome",
    ]
)
