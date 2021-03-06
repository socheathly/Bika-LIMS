from setuptools import setup, find_packages
import os

version = '3.0a3'

setup(name='bika.lims',
      version=version,
      description="Bika LIMS",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "installation.txt")).read() + "\n" +
                       open(os.path.join("docs", "CHANGELOG.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Bika Open Source LIMS',
      author='Bika Laboratory Systems',
      author_email='support@bikalabs.com',
      url='www.bikalabs.com',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.ATExtensions>=1.1a3',
          'Products.CMFEditions',
          'Products.AdvancedQuery',
          'Products.TinyMCE',
          'collective.subtractiveworkflow',
          'collective.indexing>=2.0a3',
          'collective.js.jqueryui',
          'plone.app.z3cform',
          'openpyxl',
          'plone.app.iterate',
          'xhtml2pdf',
          'magnitude',
          'jarn.jsi18n',
      ],
      extras_require = {
          'test': [
                  'plone.app.testing',
              ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
