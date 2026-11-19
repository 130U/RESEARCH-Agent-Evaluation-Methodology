# Derivations

Proofs of the article's results, in its notation and with its equation numbers. Section numbers (§) refer to the
[article](../manuscript/intervention-constrained-feedback-admission.md); every figure quoted here is recomputed
in [results](../reproduce/results.md).

| | Result | Section |
| --- | --- | --- |
| [D1](#d1-reach-and-zero-effect-outside-it) | Reach, and zero effect outside it | §2, eqs. 2.1 and 2.2 |
| [D2](#d2-the-producer-is-not-identifiable-from-the-transcript) | The producer is not identifiable from the transcript | §2, eq. 2.3 |
| [D3](#d3-exact-bounds-from-clean-runs) | Exact bounds from clean runs | §3, §5 |
| [D4](#d4-what-a-gate-does-to-precision) | What a gate does to precision | §6, eq. 6.1 |
| [D5](#d5-classes-of-invalid-feedback-and-gates-in-series) | Classes of invalid feedback, and gates in series | §6, eq. 6.2 |
| [D6](#d6-when-a-gate-pays-and-the-order-of-gates) | When a gate pays, and the order of gates | §6, eq. 6.3 |
| [D7](#d7-admissibility-is-monotone-and-every-refusal-has-an-address) | Admissibility is monotone, and every refusal has an address | §2, eq. 2.4 |
| [D8](#d8-what-each-clause-of-the-integrity-contract-removes) | What each clause of the integrity contract removes | §4, eq. 4.1 |
| [D9](#d9-what-the-acceptance-rule-guarantees) | What the acceptance rule guarantees | §7, eq. 7.1 |

---

## D1. Reach, and zero effect outside it

**Model.** A run is a structural causal model. Its variables are the components' settings and the messages
$`m_0, \dots, m_n`$. Each message is a function of its parents and of exogenous noise,

```math
m_i = f_{\pi(m_i)}\big(\mathrm{pa}(m_i),\, u_i\big), \qquad (D1.1)
```

where $`\pi(m_i)`$ is the producing component, $`\mathrm{pa}(m_i)`$ contains the settings that component reads and
the earlier messages it is shown, and $`u_i`$ collects sampling noise and seeds. An intervention on
$`ℐ`$ replaces the settings of the components in $`ℐ`$ and leaves every function and every
$`u_i`$ as it was. $`\mathrm{Reach}(ℐ)`$ is the set of messages with a directed path from some
member of $`ℐ`$ (Equation 2.1).

**Claim (Equation 2.2).** If $`m \notin \mathrm{Reach}(ℐ)`$, then $`m`$ takes the same value under
any two settings of $`ℐ`$.

**Proof.** Order the variables topologically and argue by induction along the order. Let $`m`$ have no directed
path from $`ℐ`$. Then no parent of $`m`$ is in $`ℐ`$, and no parent has a directed path from
$`ℐ`$, since such a path would extend to $`m`$. By the induction hypothesis every parent keeps its
value, $`u`$ is unchanged by assumption, and $`m`$ is a function of the two. ∎

**In the τ²-bench orchestrator.** On a fresh run with two participants,

```math
m_0 = c, \qquad m_1 = f_U(m_0,\ \text{instructions},\ u_1), \qquad m_2 = f_M(\theta,\ \text{policy},\ m_0,\ m_1,\ u_2), \qquad (D1.2)
```

with $`c`$ a constant in the orchestrator's source. The only edge out of the system prompt $`\theta`$ that
appears here is into $`m_2`$. So $`m_0 \notin \mathrm{Reach}(\{\theta\})`$, and with the seed fixed the
customer's first message $`m_1`$ is outside it too: the prompt's reach begins at turn 2. This is what the
initialization control observes on 12 tasks under three prompts, and what the archive shows across four models,
in each of whose 1,824 runs the first generated agent message is at turn 2.

**The test runs the other way.** If some change of $`\theta`$ changes $`m`$ with $`u`$ fixed, then
$`m \in \mathrm{Reach}(\{\theta\})`$. Invariance under intervention does not prove absence of a path in
general, because effects can cancel; together with the source, which shows the branch that writes $`m_0`$ taking
no argument derived from the prompt, it does.

## D2. The producer is not identifiable from the transcript

Let $`𝒯`$ be the set of transcripts, role labels included. A transcript-only gate is a function
$`g: 𝒯 \to \{\text{examine}, \text{route out}\}`$. Let $`W_1, W_2`$ be runs with the same transcript
$`\tau`$ in which the criticized message is produced by the framework and by the model. For a prompt-editing step
the correct decisions are $`\text{route out}`$ in $`W_1`$ and $`\text{examine}`$ in $`W_2`$. If $`W_1`$ occurs with
probability $`q`$ and $`W_2`$ with probability $`1-q`$, the error of $`g`$ on the pair is

```math
q\,𝟏[g(\tau) = \text{examine}] + (1-q)\,𝟏[g(\tau) = \text{route out}] \;\ge\; \min(q,\,1-q), \qquad (D2.1)
```

because $`g(\tau)`$ is one value and is wrong in one of the two runs. ∎ (Equation 2.3.) A randomized gate does no
better, since its error is a mixture of the two deterministic ones.

A gate that also reads the execution record sees different inputs in $`W_1`$ and $`W_2`$ and can be right in
both. The origin pair of §6 is this construction: the criticized sentence and the claim are the same in both
cards, the judge admitted both, and the call ledger separated them.

## D3. Exact bounds from clean runs

If an event has probability $`r`$ in each of $`n`$ independent trials, it occurs in none of them with probability
$`(1-r)^n`$. The exact one-sided upper bound at confidence $`1-\alpha`$ after a run with no event is the largest
$`r`$ that is not rejected, $`(1-r)^n \ge \alpha`$:

```math
r \;\le\; 1 - \alpha^{1/n} . \qquad (D3.1)
```

This is the Clopper–Pearson bound at zero events. At 95% confidence:

| Clean run | $`n`$ | Bound |
| --- | ---: | ---: |
| Openings unchanged by the prompt, §3 | 36 | 7.98% |
| Openings unchanged across the archive, §3 | 1,824 | 0.16% |
| Reviewer diagnoses supported on all three questions, §5 | 8 | 31.2% |

The third line reads the other way round: zero supported diagnoses in eight bounds the share of supported ones.
The bounds treat runs as independent trials; tasks repeat within each set, so they are stated as a summary of how
much a clean run of that length can show, next to the structural argument of D1, which needs no sample.

## D4. What a gate does to precision

Let $`V`$ mark a valid diagnosis and $`A`$ an admitted one, with $`\Pr[V] = p`$, $`\Pr[A \mid V] = t`$ and
$`\Pr[A \mid \bar V] = f`$. By Bayes' rule,

```math
\Pr[V \mid A] = \frac{p\,t}{p\,t + (1-p)\,f}, \qquad
\frac{\Pr[V \mid A]}{\Pr[\bar V \mid A]} = \frac{p}{1-p}\cdot\frac{t}{f} . \qquad (D4.1)
```

(Equation 6.1.) Subtracting $`p`$ gives the gain in closed form:

```math
\Pr[V \mid A] - p \;=\; \frac{p\,(1-p)\,(t - f)}{p\,t + (1-p)\,f} . \qquad (D4.2)
```

The denominator is positive whenever anything is admitted, so precision rises exactly when $`t > f`$, falls when
$`t < f`$ and is unchanged at $`t = f`$. ∎ A gate that rejects at random has $`t = f`$ and changes nothing however
much it rejects. The code checks the equivalence on a grid of 8,000 gates in exact arithmetic.

On the twelve cards $`p = 5/12`$. The judge has $`t = 5/5`$ and $`f = 2/7`$, so the gain is
$`\tfrac{5}{12}\cdot\tfrac{7}{12}\cdot\tfrac{5}{7} \big/ \tfrac{7}{12} = \tfrac{25}{84}`$ and precision is
$`\tfrac{5}{12} + \tfrac{25}{84} = \tfrac{5}{7}`$, 71.4%. With origin, $`f = 1/7`$ and precision is
$`\tfrac{5}{6}`$, 83.3%.

## D5. Classes of invalid feedback, and gates in series

Partition the invalid diagnoses into classes $`k`$ with shares $`w_k`$, $`\sum_k w_k = 1`$. Gate $`i`$ admits a
valid diagnosis with probability $`t_i`$ and one of class $`k`$ with probability $`f_{ik}`$, independently of the
other gates given the class. A diagnosis is admitted when every gate admits it, so

```math
t = \prod_i t_i, \qquad f = \sum_k w_k \prod_i f_{ik} . \qquad (D5.1)
```

(Equation 6.2.) A gate that cannot tell class $`k`$ from valid feedback has $`f_{ik} = t_i`$ and leaves that class's
term multiplied by the same factor as $`t`$: against that class its likelihood ratio is 1.

On the cards the seven invalid diagnoses fall into three classes.

| Class | Cards | Judge admits | Origin admits | Both admit |
| --- | ---: | ---: | ---: | ---: |
| Refuted | 3 | 0 of 3 | 3 of 3 | 0 |
| Insufficient, within the prompt's reach | 3 | 1 of 3 | 3 of 3 | 1 |
| Insufficient, outside the prompt's reach | 1 | 1 of 1 | 0 of 1 | 0 |

Then $`f_{\text{judge}} = \tfrac{3}{7}\cdot 0 + \tfrac{3}{7}\cdot\tfrac{1}{3} + \tfrac{1}{7}\cdot 1 = \tfrac{2}{7}`$
and $`f_{\text{both}} = \tfrac{3}{7}\cdot 0 + \tfrac{3}{7}\cdot\tfrac{1}{3} + \tfrac{1}{7}\cdot 0 = \tfrac{1}{7}`$,
the values of §6. The two gates are blind to complementary classes: the judge to the third, by D2, and origin to
the first two, by design. Neither can stand in for the other.

## D6. When a gate pays, and the order of gates

**One gate.** Per offered diagnosis, acting on everything is worth $`p\,v - (1-p)\,c`$. With a gate that costs
$`\kappa`$ it is worth $`p\,t\,v - (1-p)\,f\,c - \kappa`$. The difference is

```math
(1-p)(1-f)\,c \;-\; p\,(1-t)\,v \;-\; \kappa , \qquad (D6.1)
```

the harm removed, less the value removed, less the cost (Equation 6.3). For a gate with $`t = 1`$ and
$`\kappa = 0`$ the difference is $`(1-p)(1-f)\,c \ge 0`$, positive as soon as it refuses one invalid diagnosis.

**Break-even for the evidence gate.** Let a refused invalid diagnosis prevent a wasted candidate with probability
$`h`$, a wasted candidate costing $`K`$ tokens to test. Screening $`N`$ diagnoses costs $`N\kappa`$ and saves
$`N(1-p)(1-f)\,h\,K`$, so the gate breaks even when one candidate is prevented per $`K/\kappa`$ diagnoses. With
$`\kappa = 16{,}256`$ and $`K = 1{,}076{,}788`$ input tokens, $`K/\kappa = 66`$, and $`\kappa/K = 1.5\%`$.

**Order.** Let gate $`i`$ cost $`\kappa_i`$ and pass a share $`a_i`$ of what reaches it, independently. Running
the gates in the order $`1, 2, \dots`$ costs, per diagnosis,

```math
\kappa_1 + a_1\kappa_2 + a_1 a_2 \kappa_3 + \cdots . \qquad (D6.2)
```

Swapping two adjacent gates $`i`$ and $`j`$ changes only the two terms $`\kappa_i + a_i\kappa_j`$ and
$`\kappa_j + a_j\kappa_i`$. The first is smaller exactly when

```math
\frac{\kappa_i}{1 - a_i} \;<\; \frac{\kappa_j}{1 - a_j}, \qquad (D6.3)
```

so the cheapest order sorts the gates by cost per unit of refusal, and gates that cost nothing go first. ∎ The set
of admitted diagnoses is the same in every order, because a conjunction commutes; only the bill differs.
Integrity and origin cost zero model calls and the evidence gate one, which fixes the order
integrity, origin, evidence. In the audit of §5 one of the eight diagnoses targets a framework message, so that
order spends seven judge calls where the reverse spends eight.

## D7. Admissibility is monotone, and every refusal has an address

**Monotone.** If $`ℐ \subseteq ℐ'`$, a directed path from a member of $`ℐ`$ is a
path from a member of $`ℐ'`$, so $`\mathrm{Reach}(ℐ) \subseteq
\mathrm{Reach}(ℐ')`$. The other two conditions of Equation (2.4) do not depend on the intervention.
Hence $`A(d, ℐ) \Rightarrow A(d, ℐ')`$. ∎

**Address.** Let $`ℐ_1 \subset ℐ_2 \subset \dots \subset ℐ_K`$ be the interventions
an organization distinguishes, for example the prompt, the prompt with the framework, and the whole system
including the environment and the user simulator, with $`ℐ_K`$ reaching every message. For a diagnosis
whose behavior $`b(d)`$ is a message, the set $`\{k : b(d) \in \mathrm{Reach}(ℐ_k)\}`$ is
nonempty and, by monotonicity, an up-set, so it has a least element $`k^*(d)`$. The diagnosis is routed to
$`ℐ_{k^*(d)}`$. ∎ For the greeting, $`k^* = 2`$: the framework. For a diagnosis about the simulated
customer's behavior, $`k^* = 3`$. The gate's exits are these addresses, which is why a refusal loses nothing.

## D8. What each clause of the integrity contract removes

Equation (4.1) has five clauses, and four of them are independent. For strict parsing, type, identity and binding
there is a reply that satisfies every other clause, violates that one, and on which the benchmark's evaluator
component reads 1, so none of the four is implied by the rest. The count is implied by identity, because equal
multisets have equal sizes; it is the part of identity that is decided before any row is read.

| Clause | Reply that violates it alone | Evaluator reads 1 on |
| --- | --- | ---: |
| Strict parsing | A duplicate JSON key, the second copy complete | 40 of 40 |
| Type | One verdict given as the string "true" | 40 of 40 |
| Identity | The right number of results, one for a different assertion | 40 of 40 |
| Binding | A complete record for the same criteria, filed under another run | 40 of 40 |

In the order of §4 every clause removes replies that the clauses before it accept. Of the 440 anomalous replies,
200 pass strict parsing and the type check; of those, 95 pass the count; of those, 40 pass identity; of those,
none passes the binding. Among the replies the count removes is an empty result list, which the evaluator reads as
1 on 40 of 40.

**Why an empty reply reads 1.** A conjunction over an empty set is true: with no result to be false, "all results
met" holds. The count clause makes the conjunction range over a set of the required size, and the identity clause
makes it range over the required assertions. Without them a missing judgment and a favorable judgment are the
same value.

**Three values.** The contract returns pass, fail, unknown or not applicable. Collapsing unknown into fail would
blame the agent for the evaluator's missing output, and collapsing it into pass is the defect itself. Unknown
propagates: the acceptance rule of §7 treats an unknown judgment as a reason to keep the seed.

## D9. What the acceptance rule guarantees

Write $`q_s(x)`$ and $`q_c(x)`$ for whether the seed and the candidate qualify on validation task $`x`$ under
Equation (7.1). The rule adopts the candidate only if the optimizer selected it, every judgment and cost is known,
$`\sum_x q_c(x) > \sum_x q_s(x)`$, $`q_c(x) \ge q_s(x)`$ for every $`x`$, no critical violation is new, and the
candidate's validation tokens are at most 1.25 times the seed's.

**It never widens the optimizer's choice.** Adoption requires the optimizer's own selection, so the set of
adopted candidates is a subset of the set the optimizer would adopt.

**No regression.** If the candidate is adopted, every task the seed qualified on is a task the candidate
qualifies on, by the fourth condition.

**Qualification is stricter than the score.** $`Q`$ implies an official reward of 1, so on any set of runs the
qualified count is at most the official count, and the difference counts runs that pass on the score and fail
another term. In the final test the counts are 5 and 8.

**The decision of §7, recomputed.** With the evidence rows as input, the public function keeps the seed and
returns three reasons: the optimizer did not select the candidate, the qualified count is not higher, and a task
the seed qualified on regressed. Setting the optimizer's selection to true leaves the decision unchanged: the
last two reasons stand on their own.
