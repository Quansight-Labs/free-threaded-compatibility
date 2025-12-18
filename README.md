### What is this repository?

This repository is for coordinating ecosystem-wide work. We will use
this repository to track, understand, and provide documentation for
dealing with issues that we find are common across many
libraries. Issues that are specific to a project should be reported in
that project's issue tracker.

### Documentation

You can find documentation for various free-threading topics
on [py-free-threading.github.io](https://py-free-threading.github.io).

#### Using Intersphinx References

This documentation generates a Sphinx-compatible `objects.inv` file for cross-referencing from other projects.

**From Sphinx projects:**
```python
# conf.py
intersphinx_mapping = {
    'py-free-threading': ('https://py-free-threading.github.io/', None),
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

**Reference from other projects:**
```rst
:doc:`py-free-threading:porting-guide`
:ref:`py-free-threading:thread-safety-levels`
```

### Contributing

You can find contribution instructions in [the
documentation](https://py-free-threading.github.io/contributing/).

### License

Content in this repository is dual-licensed under the MIT and O-clause
BSD license.
