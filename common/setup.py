#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-16 18:15
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-16 18:15
 * @Desc: common
'''


from os.path import dirname, join
from sys import version_info

import setuptools

if version_info < (3, 6, 0):
    raise SystemExit("Sorry! common requires python 3.6.0 or later.")

with open(join(dirname(__file__), "common/VERSION"), "rb") as f:
    version = f.read().decode("ascii").strip()

with open("README.md", "r" ,encoding="utf8", errors="ignore") as fh:
    long_description = fh.read()

packages = setuptools.find_packages()
packages.extend(
    [
        "common",
        "common.selelogin.utils.seleniums.js",
    ]
)

requires = [
    "better-exceptions>=0.2.2",
    "selenium==3.141.0",
    "PyExecJS>=1.5.1",
    "PyMySQL>=0.9.3",
    "redis>=2.10.6",
    "requests>=2.22.0",
    "msoffcrypto-tool==4.12.0",
    "psycopg2==2.9.1",
    "psutil==5.8.0",
]

memory_dedup_requires = ["bitarray>=1.5.3"]
all_requires = memory_dedup_requires

setuptools.setup(
    name="common",
    version=version,
    author="ys-spider",
    license="MIT",
    author_email="ys.spider@yatsenglobal.com",
    python_requires=">=3.6",
    description="common是ys-spider内部使用工具库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requires,
    extras_require={"all": all_requires},
    url="https://gitlab.corp.yatsenglobal.com/spider/common.git",
    packages=packages,
    entry_points={"console_scripts": ["common = common.command.manager:execute"]},
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)