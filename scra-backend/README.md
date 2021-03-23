# Semantic Corona Rule Assistant (SCRA) – Backend Software

This directory contains the backend software (python package).

## Notes on Internal Function

Directives ("rules") are maintained as yaml-files in a repo. Upon deployment the following steps happen:

- [x] Main ontology is parsed from `world.owl.yml`.
- [x] All directives are parsed from the respective `rules.yml`-files.
- [x] The rules are integrated into the main ontology.
- [x] The reasoner is applied to this ontology. By this step implicit knowledge is made explicit via inference.
- [x] The relevant entities are converted to django-db-objects (for faster user-interaction).
