# Formalism

::: {.definition #def:keepsake title="Keepsake"}
A **keepsake** $k = (id, title, wire, tags, E, kind, \ell)$ is a declared
item of kept work, where $E$ is the tuple of required evidence labels and
$\ell$ the lapse-acceptance flag.
:::

::: {.definition #def:succession-item title="Succession item"}
A **succession item** $s = (desc, cust, tags, D)$ is a self-declared item
with description, custodian, tag set, and declared label set $D$.
:::

::: {.definition #def:verdict title="Verdict"}
A **verdict** $v$ maps a scan set to a status in
$\{KEPT, NEEDS\_PROVISION, NEEDS\_REWORK, OUTSIDE\_SCOPE\}$ with per-keepsake
findings, intake notes, review date, and registry digest.
:::

::: {.proposition #prop:fail-closed title="Fail closed"}
An empty scan set yields $OUTSIDE\_SCOPE$ with an intake note; a registry
that cannot be scored yields $NEEDS\_REWORK$ with no findings.
:::

::: {.proposition #prop:lapse-gap title="Lapse gaps are releases"}
A gap on a keepsake with $\ell = true$ reads $NEEDS\_PROVISION$, not
$NEEDS\_REWORK$.
:::
