# Publication and versioned releases

I release source only after the commands in development.md pass, figures and
formalism ledgers regenerate, reports and envelopes replay, and an independent
read-only audit checks the complete diff against the review packet.

Behavior changes require at least a minor version increment. Synchronize
pyproject.toml, the package version, CITATION.cff, .zenodo.json and the manuscript
configuration. Regenerate version-bearing artifacts, update CHANGELOG.md and
write a dated release packet with current gate results and artifact hashes.
Commit the final combined PDF, HTML pages and their local assets. Ignore
TeX intermediates, hydrated markdown, logs and transient validation reports.
Keep historical release packets and archived metadata at their original versions.

Render PDF and HTML with the template origin/main engine in an isolated export
on GitVault. Link this repository into the engine's working project layout;
never write into the active template checkout. Record the engine commit, all
commands, output checksums and visual inspection. Engine failures block release;
report them without patching the engine. An engine export is a build tool,
not a runtime or sibling-line dependency.

For source version 0.5.0, cite the repository until an archive for that exact
edition is independently verified:

> Friedman, D. A. (2026). *silver_line* (version 0.5.0) [Software source].
> <https://github.com/docxology/silver_line>

Previously verified source archive: version 0.4.0, *The Silver Line: A
Memory-and-Succession Instrument*, <https://doi.org/10.5281/zenodo.24069439>.
It identifies that source ZIP only, not version 0.5.0 or a standalone rendered
manuscript. DOI `10.5281/zenodo.22833486` remains an earlier historical archive
reference; its edition is not established by this metadata.
Keep historical titles and identifiers unchanged. A local metadata assertion is
not external publication evidence. Manual reserve-first publication is an
alternative only with owner authority for the specific object. A RESERVED DOI
is not a published deposit; verify the actual record and authorized contents
before recording a published identifier for that edition/object.

Commit on main, create an annotated vX.Y.Z tag and push main and the tag through
the GitVault repository lease. Verify both remote object identities with
git ls-remote, including the annotated tag's peeled commit. Inspect authenticated
repository hooks immediately before creating a GitHub Release. On November 8,
2026, the owner authorized this campaign with the existing public repositories'
Zenodo hooks left active. Future use requires actual owner authority for that
release and object. Verify each resulting archive's repository, tag, version,
and contents; do not prefill a DOI or amend an immutable tag to insert one
learned afterward. Without explicit archive authority, a Zenodo hook or
inconclusive inspection still blocks the Release.
PyPI, private-source disclosure, and new private-sibling deposit automation
remain unauthorized.
