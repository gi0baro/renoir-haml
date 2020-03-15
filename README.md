# Renoir-HAML

Renoir-HAML is an extension for the [Renoir engine](https://github.com/emmett-framework/renoir) providing an HAML like syntax for templates. This is not a template engine but a compiler which converts HAML files to HTML Renoir templates.

[![pip version](https://img.shields.io/pypi/v/renoir-haml.svg?style=flat)](https://pypi.python.org/pypi/Renoir-HAML) 

## Installation

You can install Renoir-HAML using pip:

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

Renoir-HAML is released under BSD license. Check the LICENSE file for more details.
