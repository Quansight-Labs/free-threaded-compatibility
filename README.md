### What is this repository?

This repository is for coordinating ecosystem-wide work. We will use
this repository to track, understand, and provide documentation for
dealing with issues that we find are common across many
libraries. Issues that are specific to a project should be reported in
that project's issue tracker.

### Documentation

You can find documentation for various free-threading topics
on [py-free-threading.github.io](https://py-free-threading.github.io).

## Using Intersphinx References

This documentation generates a Sphinx-compatible `objects.inv` file for cross-referencing from other projects.

### Reference from other project/docstrings

As for any other sphinx-based project using intersphinx you can reference
this documentation using typical rst cross linking syntax:

```rst
:doc:`porting-guide`
:ref:`thread-safety-levels`
```

You can find the names either by inspecting the html of the page, a comment will
be present just before each header; by looking at the markdown source; or running
the urls through [`intersphinx_registry reverse-lookup`](https://pypi.org/project/intersphinx-registry/), or


### Configure intersphinx for your website

For intersphinx to work, you will need to configure it to see this website;
manually:

```python
# conf.py
intersphinx_mapping = {
    "py-free-threading": ("https://py-free-threading.github.io/", None),
}
```

Or use [intersphinx_registry](https://pypi.org/project/intersphinx-registry/):

```python
# conf.py
from intersphinx_registry import get_intersphinx_mapping

intersphinx_mapping = get_intersphinx_mapping(packages={"py-free-threading"})
```

**From MkDocs with mkdocstrings:**

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          import:
            - https://py-free-threading.github.io/objects.inv
```

**Add intersphinx references to pages:**

For page-level references, use YAML frontmatter:

```markdown
---
ref: my-page-name
---

# My Page Title
```

For header-level references, use HTML comments:

```markdown
<!-- ref:my-section -->
## My Section Title
```

### Contributing

You can find contribution instructions in [the
documentation](https://py-free-threading.github.io/contributing/).

### License

Content in this repository is dual-licensed under the MIT and O-clause
BSD license.
