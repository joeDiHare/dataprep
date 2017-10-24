from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='dataprep',
      version='0.1',
      description='Submission for data challenge',
      url='http://github.com/joeDiHare/dataprep',
      long_description=readme(),
      author='Stefano Cosentino',
      author_email='@.com',
      license='MIT',
      packages=['dataprep'],
      install_requires=[
          'numpy',
          'pydicom',
          'pillow',
          'pandas'
          ],
      zip_safe=False)