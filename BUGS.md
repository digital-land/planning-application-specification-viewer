# Known viewer bugs

Observed during replica browser checks in September 2026. Both behaviours also occurred in the original viewer and were preserved during migration. Neither is a specification-package bug.

## BUG-001: Second-level component accordion stays collapsed

Status: open. Page: `/module/applicant-details/`.

Reproduce: expand “Applicant component”, then click the nested “Person obj component” control. The second-level control stays collapsed instead of revealing the person's fields. The first level opens normally. The baseline and replica showed the same behaviour.

Expected: each nested control opens and closes its own content once per activation. Investigate nested GOV.UK accordion initialisation/event handling; the cause has not yet been confirmed. Verify mouse and keyboard operation at both levels and avoid duplicate control labels.

## BUG-002: Back navigation restores search text without filtering

Status: open. Observed on the field index using the shared index-search component.

Reproduce: filter `/field/`, follow a result and use browser Back. The browser can restore the input text while the list remains unfiltered. This depends on browser navigation/form restoration behaviour and may not happen on every navigation.

Expected: the restored query, visible results, count and no-results message agree after Back/Forward navigation. Investigate page restoration events and initial filter state. Do not add URL persistence merely to fix this: the shared search did not previously provide it. The separate needs-filter controller already manages browser history and needs its own checks.
