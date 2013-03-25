from jip.dist import setup
from setuptools import find_packages

requires_java = {
    'dependencies': [
        # (groupId, artifactId, version)
        ('org.piccolo2d', 'piccolo2d-core', '1.3.1'),
        ('org.piccolo2d', 'piccolo2d-extras', '1.3.1'),
        ('org.simplericity.macify', 'macify', '1.6')
    ],
}

setup(
      name="Nengo",
      version="1.5.0",
      author="CNRGlab @ UWaterloo",
      author_email="celiasmith@uwaterloo.ca",
      description=("Create and run neural simulations using the "
                   "Neural Engineering Framework."),
      license="Mozilla 1.1",
      keywords="Neuroscience",
      packages=find_packages(),
      requires_java=requires_java,
)
