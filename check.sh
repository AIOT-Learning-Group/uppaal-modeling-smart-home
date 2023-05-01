find . -name '*.py' -exec autopep8 --in-place '{}' \;
mypy modeling --strict
mypy service --strict
mypy knowledgebase --strict
