# Standalone operation

Silver Line runs with Python 3.11 or later and the standard library.
The [development guide](development.md) lists the dev tools, system rasterizer,
native gates, and figure build. Envelope tests compare to a frozen structural
schema when another Line Set checkout is absent. See
[the binding and envelope tests](../tests/test_binding_and_envelopes.py).

Publication uses the [pinned template renderer](development.md#render-and-validate-the-manuscript)
in an isolated Git checkout. It reads the canonical
[manuscript](manuscript/README.md) and generates PDF, HTML, and validation
reports. Keep Source, native figure, and renderer artifact identities separate.

The project's whole-output ignore applies to new render outputs. Tracked native
figures remain in Source. Build new PDF and web output locally and qualify it
against the current source. Preserve [versioned release packets](releases/README.md)
and their original provenance.

Use [CITATION.cff](../CITATION.cff) or [CITATION.bib](../CITATION.bib) for source
citation. The manuscript intentionally omits a bibliography and References
section under its current publication contract.
