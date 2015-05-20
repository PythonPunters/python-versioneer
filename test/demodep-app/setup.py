
from setuptools import setup
import versioneer
commands = versioneer.get_cmdclass().copy()

setup(name="demodep-app",
      version=versioneer.get_version(),
      description="Demo",
      url="url",
      author="author",
      author_email="email",
      zip_safe=True,
      packages=["demo"],
      package_dir={"demo": "src/demo"},
      scripts=["bin/rundemo"],
      install_requires=["demodep-lib"],
      cmdclass=commands,
      )
