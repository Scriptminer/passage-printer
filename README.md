# Passage Printer

A utility tool for downloading and formatting Bible passages in various languages / versions into a printout document, to simplify the process of preparing handouts for multi-language Bible studies.

Scrapes passages from [YouVersion](https://www.bible.com/) using [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/), and formats using [Python Docx](https://pypi.org/project/python-docx/).

## Quickstart

Run in main directory, using Python3:

```python
from PrintoutFormats import generate_regular_multilingual_handout
doc = generate_regular_multilingual_handout("GEN", 11, 1, 9)
doc.save("my_passage.docx")
```

Refer to `examples.py` for further use cases.