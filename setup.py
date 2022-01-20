"""
Copyright 2021 Justin Crawford <Justin@stacksmash.net>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import io
import os
import sys
from shutil import rmtree
import setuptools

if __name__ == "__main__":
	#here = os.path.abspath(os.path.dirname(__file__))

	#with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
	with open("README.md") as f:
		long_description = '\n' + f.read()
	setuptools.setup(
			name='flapp',
			version='1.0',
			description='Language translation and formatting library',
			long_description=long_description,
			long_description_content_type='text/markdown',
			author='NightShadow',
			author_email='Justin@stacksmash.net`',
			url='https://github.com/justasic/flapp/',
			python_requires='>=3.6.0',
			packages=setuptools.find_packages(),
			classifiers=[
				"Programming Language :: Python :: 3",
				"Operating System :: OS Independent",
				"License :: OSI Approved :: MIT"
			]
	)
