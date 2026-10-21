# Formalism

::: {.definition #def:keepsake title="Keepsake"}
A **keepsake** $k = (id, title, wire, tags, E, kind, \ell)$ is a declared
item of kept work, where $E$ is the tuple of required evidence labels and
$\ell$ the registry lapse-eligibility flag, permitted only for LAPSE requirements.
:::

::: {.definition #def:succession-item title="Succession item"}
A **succession item** has an item ID, description, custodian, tag set,
declared label set and optional scoped release. A release names that exact
item ID, declarer, declaration date and source reference.
:::

::: {.definition #def:verdict title="Verdict"}
A **verdict** maps a scan set to one of KEPT, DECLARED_RELEASE,
NEEDS_PROVISION, NEEDS_REWORK or OUTSIDE_SCOPE, with item-linked findings
and notes, subject identity, review date or explicit
undated mode, registry digest/version, evaluator version, original and
normalized declaration digests, and qualified scope counts.
:::

::: {.proposition #prop:fail-closed title="Fail closed"}
An empty scan set yields $OUTSIDE\_SCOPE$ with an intake note; a registry
that cannot be scored yields $NEEDS\_REWORK$ with no findings.
:::

::: {.proposition #prop:lapse-gap title="Eligibility is not a release"}
A gap on a keepsake with $\ell = true$ reads $NEEDS\_PROVISION$, not
$NEEDS\_REWORK$, and is not a declared release. An explicit scoped release
may read $DECLARED\_RELEASE$ without a retention penalty. Restraint remains
independent. Aggregation preserves the strongest gap; a complete unrelated
item cannot compensate for another item's missing custody or restraint.
:::
