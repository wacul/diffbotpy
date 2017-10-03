from setuptools import setup, find_packages

install_requires = [
      "requests",
      "toml",
]


with open("README.md") as f:
    long_description = f.read()

setup(name='diffbotpy',
      version='0.1',
      description='diffbot client for Python',
      long_description=long_description,
      packages=find_packages(exclude=["tests"]),
      include_package_data=True,
      zip_safe=False,
      test_suite="tests",
      license="MIT",
      keywords="diffbot",
      install_requires=install_requires,
      entry_points="""
""")
