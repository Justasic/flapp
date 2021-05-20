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
import datetime
import time
import typing
import json
import warnings
from pathlib import Path

class Flapp:
	# Loaded/cached locales
	_loaded_locales = {}

	@staticmethod
	def _yaml_loader(p: Path, locale: str, fl: Flapp):
		try:
			import yaml
			if p.suffix in [".yaml", ".yml"]:
				with p.open() as fp:
					fl.add_locale(locale, fp)
		except ImportError:
			pass

	# Loaders we can use to load different files
	_loaders = {
		"yaml": _yaml_loader,
		"json": lambda p, l, fl: fl.load_locale(l, json.load(p.open())) if p.suffix == ".json" else None,
	}

	def _pluralize(self, var, arg: str) -> str:
		singular = ""
		plural = "s" if not arg else arg
		if "," in arg:
			singular, plural = arg.split(",", 1)

		# TODO: support locale-specific plurals like
		# 2 or 3 being different in some languages
		return singular if int(var) == 1 else plural

	def _yesno(self, var, arg: str) -> str:
		if not arg:
			return "yes" if var else "no"
		elif "," in arg:
			return arg.split(",")[int(bool(var))]

	def _datetime(self, var, arg: str) -> str:
		# TODO: Support locale-specific date formatting?
		if isinstance(var, datetime.datetime):
			return var.strftime(arg)
		elif isinstance(var, datetime.date):
			return var.strftime(arg)
		elif isinstance(var, float) or isinstance(var, int):
			return datetime.datetime.fromtimestamp(var).strftime(arg)
		else:
			return str(var)

	# all the pre-defined filters
	_filters = {
		"pluralize": _pluralize,
		"yesno": _yesno, 
		"datetime": _datetime, 
		"cut": lambda v,a: v.replace(a, ""), 
		"empty_if_false": lambda v,a: "" if not v else a, 
		"empty_if_true": lambda v,a: "" if v else a, 
		"default_if_none": lambda v,a: a if v == None else v, 
		"lower": lambda v,a: str(v).lower(), 
		"upper": lambda v,a: str(v).upper(), 
		"title": lambda v,a: " ".join(s.capitalize() for s in str(v).split(" ")), 
		"join": lambda v,a: a.join(v), 
	}

	def __init__(self, locale_dir: typing.Union[Path, str], file_pattern: str, default: str):
		self.default = default
		self.locales = Path(locale_dir)
		self.file_pattern = file_pattern

		if not self.locales.exists():
			raise FileNotFoundError(f"Locales folder does not exist: {self.locales}")
		if not self.locales.is_dir():
			raise NotADirectoryError(f"{self.locales} must be a folder.")

	def filter_exists(self, name: str):
		return name in self._filters

	def add_filter(self, name: str, function: callable):
		self._filters[name] = function
	
	def remove_filter(self, name: str):
		del self._filters[name]

	def locale_loaded(self, locale: str):
		return locale in self._loaded_locales

	def add_locale(self, locale: str, locale_strings: dict):
		self._loaded_locales[locale] = dict
	
	def remove_locale(self, locale: str):
		del self._loaded_locales[locale]

	def add_loader(self, name: str, loader: callable):
		self._loaders[name] = loader
	
	def remove_loader(self, name: str):
		del self._loaders[name]

	def translate(self, node: str, *args, **kwargs):
		locale = self.default if not args else args[0]

		if locale not in self._loaded_locales:
			lpath = self.locales / self.file_pattern.format(locale=locale)
			
			if not lpath.exists():
				raise FileNotFoundError(f"Locale file {lpath} does not exist!")
			if not lpath.is_file():
				raise FileExistsError(f"{self.locales} is not a file!")

			for _,loader in self._loaders.items():
				loader(lpath, locale, self)
		
		# Split the node string into an array
		path = node.split('.')
		unformatted_val = self._loaded_locales[locale]
		# This should narrow down to a string
		for p in path:
			unformatted_val = unformatted_val[p]
		
		if not isinstance(unformatted_val, str):
			raise ValueError(f"the value of {node} must result in a string not {type(unformatted_val)}!")

		# if it's just a normal string translation, return that and don't bother formatting
		if not "{" in unformatted_val:
			return unformatted_val

		# Begin parsing all the different values and filters.
		idx = unformatted_val.find("{")
		# TODO: support escaping { and }
		while idx != -1:
			endpos = unformatted_val.find("}", idx)
			# make sure exception is correct
			if endpos == -1:
				raise SyntaxError("Expected '}' but got EOF, expression begins at column %d" % idx)
			
			expression = unformatted_val[idx+1:endpos]
			replacement = ""
			variable = func = args = None
			if "|" in expression:
				variable, func = expression.split("|", 1)
				if ":" in func:
					func, args = func.split(":", 1)

			# Check if our keyword was given or not, otherwise dump a warning and replace with
			# an empty string.
			if not variable.lower() in set(k.lower() for k in kwargs.keys()):
				warnings.warn(f"{variable} has no associated data to be formatted with!", SyntaxWarning)
			else:
				# find our key name case insensitively:
				key = variable.lower()
				value = None
				for k, v in kwargs.items():
					if k.lower() == key:
						key = k
						value = v
						break
				
				# If the filter does not exist, show a warning about it and then do a normal
				# variable formatting replacement
				if not func in self._filters:
					# Only log a warning if arguments or a function was expected
					# Don't warn for simple variable replacements.
					if not isinstance(func, type(None)) or not isinstance(args, type(None)):
						warnings.warn(f"\"{func}\" specified but no filter by that name exists!", SyntaxWarning)
					replacement = value
				else:
					replacement = self._filters[func](value, args)

			unformatted_val = unformatted_val[0:idx] + str(replacement) + unformatted_val[endpos+1:]

			# Skip over the just processed formatter
			idx = unformatted_val.find("{", idx + len(str(replacement)))
		return unformatted_val