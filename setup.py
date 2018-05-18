from setuptools import setup

setup(name='PmedConnect',
      version='0.1.2',
      description='Searches and fetches results from PubMed',
      url='http://github.com/AMCeScience/PmedConnect',
      author='Allard van Altena',
      author_email='a.j.vanaltena@amc.uva.nl',
      license='GPL-3.0',
      packages=['PmedConnect'],
      install_requires=[
        'progressbar2',
        'Biopython'
      ],
      test_suite='nose.collector',
    	tests_require=[
    		'nose'
  		],
      include_package_data=True,
      zip_safe=False)