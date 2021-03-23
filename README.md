[![Build Status](https://cloud.drone.io/api/badges/cknoll/scra/status.svg)](https://cloud.drone.io/cknoll/scra)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Semantic Corona Rule Assistant (SCRA)

**Important Notices**:
- This project is currently in experimental early development an **not ready for production**!
- Obviously, the "knowledge" in this repository is at most as trustworthy as those who have write access to this repository. Especially, the assertions documented in this repository **must not be interpreted as legal advice**.


## Motivation

The COVID-19 pandemic affects many countries all over the world. With aim of containment most countries have put adopted a *set of rules* which restricts every days life. Moreover, the rules may vary considerably not only *between* countries but also *within* countries. Communicating such rules to the population is nontrivial, especially as the rules may change over time and also the regions where which rules apply. Media coverage often concentrates on "interesting" differences and suggested legislation updates which are discussed but not (yet) valid. The actutal legal documents are often impractical for most people (too long, too complicated, low relevance density). All this potential confusion which rules actually apply. Confusion, however, harms compliance with the rules and thus contributes to less effective containment and thus more societal and individual damage.

SCRA aims to mitigate these issues by providing a medium for simple, clear traceable communication of those rules which are currently relevant to the user. This is done by providing a simple web front end for accessing a knowledge base which contains a semantic representation of the rules.


## Back End: Repo-based Knowledge Base

The knowledge in this application consists of an (computational) ontology, which contains assertions about which rule applies to which geographic entity, which rule is related to which topic etc. This ontology is represented as a set of YAML-Files, which are kept under version control in a repository. This allows for easy access for both humans and computers.


## Front End: Simple Query Service

The front end allows the user to formulate a query for a concrete region (e.g. a specific district in a federal state in a country), w.r.t. a concrete topic (e.g. hotel accommodation). This query is transformed to a SPARQL-query, which can be sent to the knowledge base. Every query result (i.e. every applying rule) is shown to the user, along with the source of the information (e.g. the legal document where this rule is defined). Thus the user can check by themselves if the information is correct but do not need to read the whole document.


## Testing and Deployment

See [django/README.md](django/README.md).

## Current Status and Contributing

Currently this project is in experimental early development. Short term goal is to establish a proof of concept and then gather support for further development and content management. External contributions are very welcome! If you are interested in contributing, feel free to open an issue or [contact the author](https://cknoll.github.io/pages/impressum.html).
If you submit code please note that this project uses automatic code formatting with the tool [black](https://github.com/psf/black), more precisely: `black -l 120 src`.
