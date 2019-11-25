# Renoir-Haml

Renoir-Haml is an extension for the [Renoir engine](http://github.com/emmett-framework/renoir) providing an Haml like syntax for templates. This is not a template engine but a compiler which converts haml files to html renoir templates.

[![pip version](https://img.shields.io/pypi/v/renoir-haml.svg?style=flat)](https://pypi.python.org/pypi/Renoir-Haml) 

## Installation

You can install Renoir-Haml using pip:

    pip install renoir-haml

And add it to your Renoir engine:

```python
from renoir_haml import Haml

renoir.use_extension(Haml)
```

## Configuration

| param | default | description |
| --- | --- | --- |
| encoding | utf8 | encoding for IO |
| reload | `False` | enable auto reload on file changes |

## License

Renoir-Haml is released under BSD license. Check the LICENSE file for more details.
