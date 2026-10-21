# Publication and reserve-first release

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

Daniel reserves and mints the new Zenodo version DOI. Keep the last verified
DOI in metadata as a historical identifier until he supplies its replacement;
do not claim it identifies the new software version. No new DOI is inferred,
reserved or minted by the source release workflow.

Commit on main, create an annotated vX.Y.Z tag and push main and the tag through
the GitVault repository lease. Verify both remote object identities with
git ls-remote, including the annotated tag's peeled commit. A GitHub Release
object is permitted only when the authenticated repository-hooks API shows no
Zenodo hook. An inconclusive check or a Zenodo hook means no Release object;
the pushed source tag still completes the source release. No workflow here
publishes a Zenodo deposit automatically.
