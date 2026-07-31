# Bounded autonomy

Agents should be allowed to move quickly inside an approved boundary, not to create unlimited review, design, or scope loops.

## Circuit breaker

For a design or final review phase:

1. Attempt one identifies blockers tied to an unsafe or unimplementable outcome inside declared scope.
2. The author may make one correction targeted to named findings.
3. A second non-pass stops autonomous remediation.
4. An operator chooses one: simplify the outcome, accept a named risk, supply missing context, or re-anchor/split the work.

A reviewer may offer advisory suggestions. Advisory suggestions do not make a review fail and do not justify an unbounded loop.

## Re-anchor rather than patch around architecture

Return to design when a finding reveals a new architectural, state, transaction, or security class. Repeatedly adding denylists or conditionals to avoid the same class of defect is not remediation; it is evidence the task boundary is wrong.
