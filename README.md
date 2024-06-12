# Passage Printer

A utility tool for downloading and formatting Bible passages in various languages / versions into a printout document, to simplify the process of preparing handouts for multi-language Bible studies.

Run in python using:

```python
from PrintoutFormats import generate_regular_multilingual_handout
doc = generate_regular_multilingual_handout("GEN", 11, 1, 9)
doc.save("my_passage.docx")
```

Refer to `examples.py` for further use cases.