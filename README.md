# Flapp

Flapp is the ultimate translation system for your project. It is intended to correctly
translate all strings in a program to any language without needing to add multiple
strings for the same sentence just to make something plural. This also allows for
locale-specific dates and times, pluralization, and potentially even conditionals
which enables advanced formatting!

Localization is nothing more than a string lookup system from a set of files which
you can specify the system for looking up those file names. The translate function
takes a string which contains a sequence of filters inside the translatable string.
These `filters` are similar to [Django template filters](https://docs.djangoproject.com/en/3.2/topics/templates/#filters)
that allow for flexible string generation for translation.

Syntax for all filters is as follows:
`{VARIABLE|filter:filter "arguments"}`
, the variable names are case insensitive.

## Setup
```bash
python setup.py install
```

## Usage

Assume there is a file `translations.en_US.yml` in the folder `locales` which exists with the content:
```yaml
user:
    hello-message: "Hello, {USERNAME|title}! It is {NOW|date:\"D d M Y\"}!"
```
and `translations.ru_RU.yml` in the same folder:
```yaml
user:
    hello-message: "Привет, {USERNAME|title}! Сегодня {NOW|date:\"D d M Y\"}!"
```

To format/translate a string:
```python
>> from flapp import Flapp
>> from datetime import datetime
>> translator = Flapp("/path/to/locales", file_pattern="translations.{locale}.yml", default="en_US")
>> translator.translate("user.hello-message", username="flapper", now=datetime.now())
Hello, Flapper! It is Wed 09 Jan 2008!
>> translator.translate("user.hello-message", "ru_RU", username="flapper", now=datetime.now())
Привет, Flapper! Сегодня Wed 09 Jan 2008!
```

The translate function takes a "node" which represents the path to the string. See [Loading other formats](#Loading-other-formats) below.

The second argument to `translate` is used to specify a locale different from the default locale, this locale is used to find and load the
locale file if it is not already loaded.

## Built-in filters

There are some basic filters that come included:

| filter | Description | Arguments | Default |
| ----------- | ----------- | ----------- | ----------- |
| `pluralize` | Add text if a number is greater than 1 | comma separated list based on count | "s" if plural |
| `yesno` | Convert a boolean value to the language's boolean representation | comma separated pair in place of "no,yes" | "yes" or "no" |
| `datetime` | Format the variable as a datetime string | strftime-compatible format string | datetime default formatt |
| `cut` | Removes text from a variable | quoted string of text to remove | *N/A* |
| `empty_if_false` | Returns an empty string if the variable evaluates to False | value returned if True | *N/A* |
| `empty_if_true` | Returns an empty string if the variable evaluates to True | value returned if False | *N/A* |
| `default_if_none` | Returns a default value if the variable is False/None | default value | *N/A* |
| `lower` | Convert the variable to all lowercase | *N/A* | *N/A* |
| `upper` | Convert the variable to all uppercase | *N/A* | *N/A* |
| `title` | Convert the variable to titlecase (capitalize the first letter of every word) | *N/A* | *N/A* |
| `join` | Join a list together with a deliminator | deliminator string | ", " |

You can also add your own filters if you need to do some special formatting. The `variable` to be formatted and the filter's arguments
are passed as strings to the bound function. An example:
```yaml
user:
    hello-message: "Hello {WHO|memecase}!"
```

```python
>> from flapp import Flapp
>> from random import choice
>> translator = Flapp("/path/to/locales", identifier="translations.{locale}.yml", default="en_US")
>> def memecase(variable, argument: str):
>>    return ''.join(choice((str.upper, str.lower))(c) for c in str(variable))
>> translator.add_filter('memecase', memecase)
>> translator.translate("user.hello-message", who="World")
Hello WoRLd!
```

Note that the type of `variable` in the `memecase` function is undefined as it leaves it up to the `memecase` function
to return a correctly formatted string. Any data returned from the function will be cast as a string regardless.

# Loading other formats

While Yaml and JSON files are supported by default, you can load the same
data from other sources by calling `add_locale` with a dictionary to that
of what `json.loads()` would return. The node can be deliniated by a period (`.`)
and each part of the node is then used as the key for the recursive dictionaries.
An example from the above example code effectively does:

```python
>> yamldata['user']['hello-message']
Hello, {USERNAME|title}! It is {NOW|date:\"D d M Y\"}!
```

You can verify if a locale is loaded using `locale_loaded("en_GB")` and you can unload
loaded locales with `remove_locale("en_GB")` (replacing "en_GB" with the locale format you're using)

---

## License
Copyright *2021 Justin Crawford <Justin@stacksmash.net>*

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
