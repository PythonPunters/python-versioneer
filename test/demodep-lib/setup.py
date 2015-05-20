
from setuptools import setup
import versioneer
commands = versioneer.get_cmdclass().copy()

setup(name="demodep-lib",
      version=versioneer.get_version(),
      description="Demo",
      url="url",
      author="author",
      author_email="email",
      zip_safe=True,
      packages=["demolib"],
      package_dir={"demolib": "src/demolib"},
      cmdclass=commands,
      )
