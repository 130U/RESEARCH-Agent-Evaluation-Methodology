# Agent Evaluation Methodology: Intervention-Constrained Feedback Admission

**Independent research**  
Letao (Theodore) Ouyang · May – September 2026

**Materials.** The experiments use τ²-bench retail at revision `2174a60` and the GEPA optimizer at revision `15ee314`. The agent, the simulated user, the benchmark's reviewer and the judges ran on gpt-5.6-sol at low reasoning effort. Reference labels were assigned by independent model reviewers and fixed before each gate ran. The archive census of Section 3 reads the result files published by the benchmark's authors and calls no model. Every figure below is recomputed from the files in [`evidence/`](../evidence) by [`reproduce/run_all.py`](../reproduce/run_all.py).

## Summary

A reflective optimizer reads a failed trace, a reviewer explains the failure, and the explanation becomes the next prompt. The loop assumes that the thing criticized is the thing being changed. I found the assumption failing in a widely used benchmark: in τ²-bench retail the first assistant message of every conversation is written by the framework before the model is called, a reviewer faulted the agent for it, and a judge instructed to check the evidence accepted the fault with the words "the actor controlled that response". No edit to the prompt can change that message. In the benchmark's public archive the same sentence opens all 1,824 runs and accounts for 7.34% of the 24,836 messages labelled `assistant`.

I built Intervention-Constrained Feedback Admission (ICFA) to repair the loop. A diagnosis is treated as a claim that has to pass four gates in order, each removing a different way of being wrong and each with its own exit: the evaluation record is complete, the criticized message was produced by a component the current intervention can reach, the claim is supported by what the agent could see when it acted, and the changed strategy qualifies on more than the score. Admissibility is a relation between a diagnosis and an intervention, so a diagnosis that leaves through the second gate is routed to the framework's owner with nothing lost.

## Problem and Approach

In May 2026 I set out to connect τ²-bench, whose retail domain supplies a policy, tools, a database and a simulated customer, to GEPA, which improves a prompt by reflecting on traces. The benchmark already ships a reviewer that names the faulty turn, attributes it to the agent or the user and proposes a correction. Feeding that reviewer to the optimizer is the obvious design, and it is the design the reflective-optimization literature assumes. I asked a prior question: what must be true of a diagnosis before it is allowed to change the agent?

The answer has four parts, and they are independent. A score can be read only if the record behind it is complete. A message can be attributed to the prompt only if the prompt produced it, which the transcript cannot show. A fault can be assigned only on what was visible at the moment of action. And an edit can be kept only if the result is right in every respect a customer would care about, of which the benchmark's score checks some. I implemented each part as a gate with a three-valued outcome, connected the gates to GEPA through an adapter that changes nothing else, and measured each gate separately: on the benchmark's own evaluator with controlled inputs, on every message of my own runs, on the public archive, on the reviewer's diagnoses as they occurred, on six minimal pairs of diagnoses that differ in one factor, and on a candidate that the optimizer wrote and the benchmark passed.

The study measures the gates: what each admits, what it sends elsewhere and what it costs. The gate code, its 137 tests, the evidence files and a script that recomputes every figure are public.

## Key Contributions

* **I separated three facts that a transcript shows as one.** The role label on a message, the component that produced it and the component the current optimization step may change are different properties. I proved that the second cannot be recovered from the transcript: two runs with identical transcripts and different producers force any transcript-only gate to err on one of them (Equation 2.3), and I built the pair that shows it.
* **I defined admissibility as a relation between a diagnosis and an intervention.** A diagnosis is admissible for an intervention only if the criticized behavior lies in the intervention's reach (Equation 2.4). Reach is a necessary condition for any effect, it is decided from execution records at zero model calls, and a diagnosis outside it is routed to the smallest intervention that contains it.
* **I measured origin on public data.** In the 1,824 published runs of τ²-bench retail, across four agent models, every conversation opens with one framework-written sentence carrying the `assistant` label: 1,824 of 24,836 assistant-role messages, with 23,012 bound to a generation record and none left unknown. In 1,801 of the runs the model's first action of its own is the authentication step the opening is faulted for omitting.
* **I showed that a capable judge reading the evidence does not close the gap.** Of the eight diagnoses the benchmark's reviewer produced on 18 runs, none was fully supported under labels fixed beforehand; the evidence gate rejected five, abstained on two and admitted one, the framework's greeting.
* **I isolated what the origin gate adds.** On six minimal pairs, the judge admitted every supported diagnosis and no refuted one, and admitted two of four whose evidence was insufficient. Intersecting with origin removed one of the two. The pair that differs only in who produced the text was admitted twice by the judge and separated by origin.
* **I wrote the integrity contract under which a missing result is never a pass.** On 560 controlled outputs fed to the benchmark's own assertion evaluator, the contract kept all 120 valid records and held all 440 anomalous ones as unknown; the evaluator's component read 1 on 360 of the 440.
* **I separated admission from acceptance.** A candidate that GEPA wrote passed both validation tasks on the official score while promising a refund deadline the policy does not give; it qualified on one of two. In the public archive, agents named a poem for a customer in 10 of the 16 runs of one task, against the policy's rule on outside knowledge, and 9 of the 10 received the full reward.
* **I priced the gates.** Integrity and origin cost no model call. The evidence gate costs 16,256 input tokens per diagnosis, 1.5% of the 1,076,788 it took to test one candidate, so it pays for itself if it prevents one wasted candidate in 66 diagnoses.

## Manuscript

### 1. A reflective optimizer changes what it is told to change

Reflective optimizers turn language into the gradient. GEPA samples trajectories, reflects on them in natural language to diagnose problems, proposes and tests prompt edits and keeps a Pareto front of its attempts; across six tasks it outperforms a reinforcement-learning baseline by 6% on average while using up to 35 times fewer rollouts (Agrawal et al., 2025). TextGrad, ProTeGi, OPRO and the DSPy optimizers share the structure: a failure is explained in words, and the words become the edit. The explanation is therefore the object on which everything depends, and the recent literature has turned to its quality.

The findings are consistent. On the Who&When dataset the best automated method identifies the responsible agent in 53.5% of failures and the decisive step in 14.2% (S. Zhang et al., 2025). Shen et al. (2026) restart agents from intermediate states of failed runs and find that for 66% of the steps that frontier judges label as the first mistake, the probability of success does not drop at that step, and that restarting at a judge's label does not help. Pisupati et al. (2026) ask people to grade the critiques that judges write on τ-bench trajectories and need a third category, "should not have flagged". The responses have followed the same line: curate which tasks reach the optimizer (Yu et al., 2026), verify by intervention which agent's prompt resolves a failure (Chu et al., 2026), gate candidates on quality and on regression (Jiang et al., 2026; Xu et al., 2026), and restrict critiques to what was observable at the action (Saeidi et al., 2026).

Each of these asks whether a diagnosis is true, or whether acting on it helps. Neither question is the first one. A diagnosis can be true and still have no claim on the component being edited, because that component did not produce the behavior. Whether it did is a fact about the execution, and a transcript does not carry it.

The case that showed me this is small. The retail policy says that at the beginning of the conversation the agent has to authenticate the user. A reviewer read a trace that begins

> **assistant:** Hi! How can I help you today?

and wrote that the agent "first asked how it could help rather than initiating authentication". The correction it proposed was to begin by requesting the account email. A judge that I had instructed to use only the policy, the tools and the messages before the action accepted the diagnosis: "The actor controlled that response." It did not. The orchestrator inserts that sentence before the first model call, the first call goes to the simulated user, and the agent's first generated message, at turn 2, asks the customer to authenticate.

### 2. Three facts about a message

Let a run of an agent system produce a transcript $`m_0, m_1, \dots, m_n`$. Three functions are defined on its messages.

The **role label** $`\rho(m) \in \{\text{assistant}, \text{user}, \text{tool}\}`$ is what the transcript shows. The **producer** $`\pi(m)`$ is the component whose execution emitted the message: the model under the agent's prompt, the framework, the user simulator or a tool. The **reach** of an intervention is defined on the system's causal graph. Let $`ℐ`$ be the set of components the current optimization step may edit; in this study $`ℐ = \{\theta\}`$, the agent's system prompt. Then

```math
m \in \mathrm{Reach}(ℐ) \iff \text{there is a directed path from some } c \in ℐ \text{ to } m . \qquad (2.1)
```

A message produced by the model under the prompt is in the reach of $`\{\theta\}`$. A constant the framework writes before the prompt is read is not. Reach is the controllability of control theory (Kalman, 1960) stated for a compound system, and the interventionist reading of cause (Woodward, 2003; Pearl, 2009) gives its consequence at once.

**Zero effect outside the reach.** Fix everything exogenous to the run. If $`m \notin \mathrm{Reach}(ℐ)`$, then for any two settings $`\theta, \theta'`$ of the components in $`ℐ`$,

```math
m(\theta) = m(\theta') . \qquad (2.2)
```

A diagnosis whose correction is "make $`m`$ different" therefore has no route to its target within $`ℐ`$. The statement is testable from the other side: change $`\theta`$, hold the rest, and compare $`m`$. Invariance under intervention is the criterion Peters, Bühlmann and Meinshausen (2016) use to identify causes; here it identifies what a prompt cannot cause.

**The producer is not identifiable from the transcript.** Take two runs $`W_1`$ and $`W_2`$ with the same transcript, role labels included, in which a message $`m`$ is produced by the framework in $`W_1`$ and by the model in $`W_2`$. A gate $`g`$ that reads only the transcript returns $`g(W_1) = g(W_2)`$. For a prompt-editing step the right decisions differ: route the diagnosis out in $`W_1`$, examine it in $`W_2`$. If the two occur with probabilities $`q`$ and $`1 - q`$,

```math
\Pr[\,g \text{ errs}\,] \;\ge\; \min(q,\, 1 - q) \quad \text{for every transcript-only gate } g . \qquad (2.3)
```

The bound does not depend on the judge's capability. A stronger judge reads the same characters. What removes the error is a record of the execution: which call produced which message.

**Admissibility.** A diagnosis $`d`$ criticizes a behavior $`b(d)`$ in a run. I define it as admissible for $`ℐ`$ when three conditions hold:

```math
A(d, ℐ) \;=\; \underbrace{C(d)}_{\text{record complete}} \;\wedge\; \underbrace{b(d) \in \mathrm{Reach}(ℐ)}_{\text{reachable}} \;\wedge\; \underbrace{S(d)}_{\text{supported at action time}} . \qquad (2.4)
```

Each condition takes the values true, false and unknown, and unknown is kept as unknown. Two properties follow from the definition. Admissibility is monotone in the intervention: if $`ℐ \subseteq ℐ'`$ then $`A(d, ℐ) \Rightarrow A(d, ℐ')`$, so a diagnosis refused for the prompt may be admitted for the framework. And every refusal has an address: the diagnosis goes to the smallest intervention whose reach contains $`b(d)`$. Nothing is discarded; it is delivered to whoever can act on it.

Responsibility and blame have a formal literature (Halpern and Pearl, 2005; Chockler and Halpern, 2004), and multi-agent optimizers assign credit among agents' prompts by contrasting rollouts or by intervening on one agent at a time (Zehle, 2026; Z. Zhang et al., 2025; Chu et al., 2026). Those methods ask which editable component should change. Equation (2.4) asks first whether the behavior belongs to an editable component at all, and answers from records without a rerun.

### 3. Origin can be established message by message

The origin gate implements the middle condition of Equation (2.4) for the τ²-bench text orchestrator. It uses positive rules only. A message is the model's when it carries the identity of exactly one agent call in the run's call ledger and its text, tool names and tool arguments equal that call's output. A message is the framework's when the run is fresh and has two participants, the message sits at turn 0 with the orchestrator's constant as its text, no generation metadata and zero cost, and the first call in the ledger is the user simulator reading that constant. Everything else is unknown, and unknown is not treated as the model's.

**My own runs.** In the 18 completed development runs over 12 tasks, all 181 assistant-role messages were bound: 18 to the framework and 163 to the model, 100 of them tool calls. The call ledger holds 248 calls, 163 by the agent, 81 by the user simulator and 4 by the assertion judge, and the 163 agent calls match the 163 messages one to one.

**An intervention on the prompt.** Equation (2.2) predicts that the opening message is invariant to the prompt. I ran the official initializer on the same 12 tasks under three system prompts: the unmodified one, the seed strategy of the optimization experiments, and a prompt that says, "At the start of the conversation, request the user's account email before giving a general greeting." The initializer received three different prompts and produced the same opening in all 36 initializations, with generation blocked and zero model calls. Read as a clean run, 36 of 36 bounds the probability that a prompt alters the opening below 7.98% at 95% confidence; read as code, the branch that writes the message never consults the prompt.

**The public archive.** The benchmark's authors publish result files for four agent models on the 114 retail tasks with four trials each. I verified the four files against their Git blob hashes and classified every assistant-role message with the same rules, using the generation record that the archive stores with each message.

**Table 1. Origin of every assistant-role message in the public archive.**

| | Runs | Assistant-role messages | Framework | Model | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: |
| claude-3-7-sonnet | 456 | 6,743 | 456 | 6,287 | 0 |
| gpt-4.1 | 456 | 5,560 | 456 | 5,104 | 0 |
| gpt-4.1-mini | 456 | 6,124 | 456 | 5,668 | 0 |
| o4-mini | 456 | 6,409 | 456 | 5,953 | 0 |
| **Total** | **1,824** | **24,836** | **1,824** | **23,012** | **0** |

One message in 13.6 that the archive labels `assistant` was not written by the model under test, 7.34% of the total, and it is the same sentence 1,824 times. The first generated agent message is at turn 2 in every run. Four different models produce four different conversations and one identical opening, which is the invariance of Equation (2.2) observed across models; as a clean run it bounds the rate of exceptions below 0.16%.

The archive also shows what a reader of role labels would get wrong. The opening is faulted for not authenticating. In 1,801 of the 1,824 runs, 98.7%, the model's first action of its own is an authentication step: a request for the email or the name and ZIP code, or an identity lookup. The behavior the diagnosis asks for is already there, one turn later, in the first message the prompt can reach.

An audit of two public leaderboards from their published artifacts, released two months after these experiments ended, found grader-written actions stored as agent actions and recommended tagging the origin of every stored action (Liu, 2026). The census above measures how much of one archive that affects, and the gate turns the tag into a decision.

### 4. The integrity contract: a missing result is never a pass

Before a diagnosis is examined, the score that prompted it has to be interpretable. The retail tasks carry natural-language assertions that a judge model evaluates, and the judge's reply is parsed and aggregated. I wrote the contract that the parsed reply must satisfy, in the sense of Meyer (1992), and gave it the fail-safe default of Saltzer and Schroeder (1975): when the record does not establish a pass, the status is unknown.

Let $`E`$ be the multiset of expected assertions and $`R`$ the parsed results. The record is complete when

```math
\begin{gathered}
\underbrace{R \text{ parses strictly}}_{\text{no duplicate keys}} \;\wedge\; \underbrace{\left\vert R\right\vert = \left\vert E\right\vert}_{\text{count}} \;\wedge\; \underbrace{\{\!\{ r.\text{assertion} \}\!\} = E}_{\text{identity}} \\
\wedge\; \underbrace{\forall r:\ r.\text{met} \in \{\text{true}, \text{false}\},\ r.\text{reason} \neq \varnothing}_{\text{type}} \;\wedge\; \underbrace{\text{binding}(R) = \text{binding}(\text{request})}_{\text{same run, task, criteria, evaluator}} .
\end{gathered} \qquad (4.1)
```

A complete record is a pass when every result is met and a fail otherwise. An incomplete record is unknown. A task with no assertions is not applicable.

I tested the contract on the benchmark's own evaluator classes, replacing only the judge's raw reply. Each of the 40 tasks that carry assertions received 14 controlled replies: three valid ones and eleven anomalies.

**Table 2. Contract status of fourteen controlled judge replies on 40 tasks.**

| Reply | Inputs | Evaluator component reads 1 | Contract status |
| --- | ---: | ---: | --- |
| Complete, all met | 40 | 40 | pass |
| Complete, one not met | 40 | 0 | fail |
| Complete, reordered | 40 | 40 | pass |
| Results field missing | 40 | 40 | unknown |
| Empty results | 40 | 40 | unknown |
| One result omitted | 40 | 40 | unknown |
| One result repeated in place of another | 40 | 40 | unknown |
| Result for a different assertion | 40 | 40 | unknown |
| Verdict as a string | 40 | 40 | unknown |
| Verdict as an integer | 40 | 40 | unknown |
| Malformed JSON | 40 | exception | unknown |
| Wrong top-level type | 40 | exception | unknown |
| Duplicate JSON key | 40 | 40 | unknown |
| Record filed under another run | 40 | 40 | unknown |

The contract kept all 120 valid records, 80 passes and 40 fails, and held all 440 anomalous replies as unknown. On 360 of the 440 the evaluator's assertion component read 1, and on the other 80 it raised an exception. The cause of the 1 on an empty reply is ordinary: a conjunction over no results is true. The 74 tasks without assertions were returned as not applicable.

Each clause of Equation (4.1) removes replies that the clauses before it accept. With strict parsing and the type check alone, 200 of the 440 anomalous replies are accepted. Adding the count leaves 95, adding identity leaves 40, and only the binding to the request removes the last 40, the records filed under another run. Strict parsing, type, identity and binding are each independent of the rest; the count, which identity implies, is decided before any row is read. The check takes a median of 10.9 microseconds.

The result is one instance of a pattern that others have documented at the level of whole benchmarks. Zhu et al. (2025) report that τ-bench counted empty responses as successful and that such issues change measured performance by up to 100% in relative terms. Xia et al. (2026) find a renderer that dropped every structured tool call and left 53 of 60 judged steps blank while every hash matched. Bellibatlu, Wang and Zhang (2026) check tools against the contracts their interfaces advertise. The contract here sits at the narrowest point, between one judge's reply and one score, where it costs nothing and decides whether anything downstream may be believed.

### 5. Evidence at the moment of action

The evidence gate judges a diagnosis against the action-time view: the policy, the tool definitions, the messages before the criticized action and the action. Later messages, raw model responses and the task's reference answer are excluded by construction, and the view is content-addressed, so altering anything after the action leaves its hash unchanged. The exclusion matters because the benchmark's reviewer reads the whole task, reference included. Knowledge of an outcome changes what an evaluator believes was foreseeable (Fischhoff, 1975) and how it grades the decision (Baron and Hershey, 1988); Saeidi et al. (2026) build critiques under partial observability for the same reason.

A judge receives the diagnosis and the view and answers three questions: is the claim supported by the visible evidence, is the agent responsible, and could the proposed correction have been chosen from what was visible. It admits only when all three hold and it can quote the policy text it relies on. A refuted claim is rejected. Anything else is an abstention. The admitted diagnosis is passed on verbatim, so the gate selects and never rewrites.

**The reviewer's diagnoses as they occurred.** I ran the benchmark's reviewer on all 18 completed runs. Six runs drew a diagnosis, eight diagnoses in all, each attributed to the agent. Before the gate ran, two independent model reviewers labelled each diagnosis on the three questions, agreeing on 20 of the 24 judgments, and an adjudication settled the rest.

**Table 3. Gate decisions on the reviewer's eight diagnoses.**

| Reference label | Diagnoses | Gate: reject | Gate: abstain | Gate: admit |
| --- | ---: | ---: | ---: | ---: |
| Supported on all three | 0 | 0 | 0 | 0 |
| Insufficient | 6 | 3 | 2 | 1 |
| Unsupported | 2 | 2 | 0 | 0 |
| **Total** | **8** | **5** | **2** | **1** |

None of the eight diagnoses was supported on all three questions. With zero in eight, the share of fully supported diagnoses in the reviewer's output is below 31.2% at 95% confidence, and the optimizer in the standard design would have reflected on all eight. The gate kept seven out. Several of the rejected diagnoses contain advice that is executable, for example to look the order up instead of asking the customer for its number; what the evidence did not establish was that the agent was at fault for not doing so.

The one admitted diagnosis is the greeting of Section 1. The labels had it as insufficient; the judge found all three questions satisfied. Its text is correct on the policy and wrong on the producer, and Equation (2.3) says a judge reading the view cannot tell. The origin gate routes it to framework review.

Two further diagnoses reached the gate in a later batch of four runs, and both were rejected for the reason the gate exists. One faulted the agent for not rerouting an order to a fallback address that the customer had not yet mentioned. The other settled which of two orders was "the older one" from the task's reference actions, when no tool result carried an order date. Both tasks had failed, and in both the diagnosis rested on information the agent had not been given.

### 6. What the origin gate adds to a judge

The eight natural diagnoses contain no fully supported case, so they cannot show what the gates do to good feedback. I built twelve diagnoses for that purpose, as six minimal pairs. In five pairs the two members share the claim and differ in one factor: whether the customer's confirmation is present in the prefix, whether the correction is allowed by the policy, whether the correction imports a later choice of the customer, whether it relies on a balance no tool returned, and whether the indexed action is the write or a read that precedes it. In the sixth pair the criticized sentence and the claim are word for word the same, and the sentence comes from the framework at turn 0 in one card and from the model later in the conversation in the other. Cards, order and reference tiers were fixed before the judge was called, the tiers confirmed by an independent model reviewer working from an anonymized packet.

**Table 4. Judge and origin gate on twelve constructed diagnoses.**

| Reference tier | Cards | Judge admits | Judge rejects | Judge abstains | Admitted after origin |
| --- | ---: | ---: | ---: | ---: | ---: |
| Supported | 5 | 5 | 0 | 0 | 5 |
| Unsupported | 3 | 0 | 3 | 0 | 0 |
| Insufficient | 4 | 2 | 1 | 1 | 1 |
| **Total** | **12** | **7** | **4** | **1** | **6** |

The judge kept every supported diagnosis and refused every refuted one. Its errors are in the middle tier: it admitted two diagnoses whose evidence was insufficient, and both are the claim of Section 1, "The assistant used a general greeting instead of authenticating the customer at the beginning of the conversation", attached to the sentence "Hi! How can I help you today?". In one card the ledger shows the framework writing the sentence; in the other the model generates the same sentence. The judge admitted both. The origin gate routed the first to framework review and passed the second on, which is the construction of Equation (2.3) carried out: one text, two producers, a transcript-only decision that cannot differ, and a record that separates them.

**The arithmetic of a gate.** Let $`p`$ be the share of valid diagnoses offered to a gate, $`t`$ the share of valid ones it admits and $`f`$ the share of invalid ones it admits. The share of admitted diagnoses that are valid is the positive predictive value of diagnostic testing (Altman and Bland, 1994):

```math
\Pr[\text{valid} \mid \text{admitted}] \;=\; \frac{p\,t}{p\,t + (1 - p)\,f}, \qquad \frac{\Pr[\text{valid} \mid \text{admitted}]}{\Pr[\text{invalid} \mid \text{admitted}]} \;=\; \frac{p}{1 - p} \cdot \frac{t}{f} . \qquad (6.1)
```

Precision rises exactly when $`t > f`$. Rejecting more proves nothing; a gate earns its place by the ratio $`t/f`$. On the cards the judge alone gives $`t = 5/5`$ and $`f = 2/7`$, so 5 of the 7 it admits are supported, 71.4%. With origin, $`f = 1/7`$ and 5 of 6 are supported, 83.3%, with $`t`$ unchanged.

Invalid diagnoses are of different kinds, and a gate sees some kinds and is blind to others. Let the invalid diagnoses fall into classes $`k`$ with shares $`w_k`$, and let gate $`i`$ admit class $`k`$ at rate $`f_{ik}`$. For gates that decide independently given the class,

```math
t \;=\; \prod_i t_i, \qquad f \;=\; \sum_k w_k \prod_i f_{ik} . \qquad (6.2)
```

A gate blind to class $`k`$ treats it as valid, $`f_{ik} = t_i`$, and contributes nothing against it. By Equation (2.3) the judge is blind to the class "outside the reach" whenever the text is the same. The origin gate has $`f = 0`$ on that class and $`t = 1`$ on everything the prompt can reach, wherever the records decide: it removes one class of invalid feedback completely and takes no valid feedback with it. The remaining admitted error, the model-produced greeting, is of another class, an attribution on insufficient evidence, and is the judge's to improve.

**When a gate pays.** Let an admitted valid diagnosis be worth $`v`$, an admitted invalid one cost $`c`$, and the gate cost $`\kappa`$ per diagnosis. Running the gate is worth it when the harm removed exceeds the value removed plus the cost:

```math
(1 - p)(1 - f)\,c \;-\; p\,(1 - t)\,v \;-\; \kappa \;>\; 0 . \qquad (6.3)
```

For the origin gate $`\kappa`$ is zero model calls and $`t = 1`$, so the condition holds whenever one diagnosis is outside the reach. For the evidence gate the measured cost is 130,049 input tokens over 8 diagnoses, 16,256 each, and 15,243 each on the twelve cards. The harm of an admitted invalid diagnosis is at least a wasted candidate: testing the one candidate of the native arm in Section 7 took four episodes and 1,076,788 input tokens. The gate's cost is 1.5% of that, so it breaks even if it prevents one wasted candidate in every 66 diagnoses it screens. The same ordering argument puts the free gates first. The outcome of a conjunction does not depend on the order of its terms, and its cost does: a judge call is spent only on diagnoses that integrity and origin have let through. In the experiments I ran the judge on every diagnosis and intersected afterwards, so that each gate's decisions are observed on the full set.

### 7. Admission is not acceptance

Admission decides whether feedback may guide an edit. Whether the edit is kept is a separate decision with separate evidence. I call a run **qualified** when five things hold together:

```math
Q \;=\; \underbrace{\text{reward} = 1}_{\text{official}} \;\wedge\; \underbrace{\text{record complete}}_{\text{Equation 4.1}} \;\wedge\; \underbrace{\text{answer sound}}_{\text{against the policy}} \;\wedge\; \underbrace{\text{user valid}}_{\text{followed its instructions}} \;\wedge\; \underbrace{\text{no critical violation}}_{} . \qquad (7.1)
```

A candidate replaces the seed strategy only if it qualifies on strictly more validation tasks, regresses on none, introduces no critical violation and stays within 1.25 times the seed's token cost. Unknown judgments and unknown costs keep the seed.

**A candidate the benchmark passed.** I gave GEPA one proposal per arm on two training tasks, with two validation tasks and six test tasks held apart. In the arm that reflects on the reviewer's diagnoses, the seed strategy passed one training task of two, the reviewer produced a diagnosis, and GEPA wrote a 2,214-character candidate that passed both training tasks. On validation the candidate scored 2 of 2 on the official reward, the same as the seed. In one of the two it had cancelled two orders, filed one return and closed with:

> The total refund is $8,276.23. The PayPal refunds should be processed within 5–7 business days.

The policy gives that deadline for cancellations. For a return it says the customer "will receive an email regarding how to return items". The candidate had extended a promise to a case the policy does not cover, both reviewers marked the answer unsound, and the candidate qualified on 1 of 2 where the seed qualified on 2 of 2. GEPA kept the seed because the official score tied. Its selection sees that score alone, and on that score the candidate was the seed's equal. The acceptance rule sees the unsound answer and keeps the seed for two further reasons: a qualified count that is not higher, and a regression on a task the seed qualified on.

In the arm that reflects on admitted diagnoses only, the seed passed both training tasks, the reviewer produced no diagnosis, and the candidate GEPA wrote from the policy alone matched the seed on training and was not adopted. Two of the four tasks changed outcome between the two arms' runs of the identical seed strategy, which is the size of the noise a one-task training gain has to be read against.

**The score's coverage.** The final test ran the selected strategy, the seed in every arm, on six held-out tasks. Of the 18 completed runs, 8 passed on the official reward and 5 qualified. The three that passed and did not qualify are the three runs of one task, in which the simulated customer first asks the agent to name a poem from its first line. The policy says the agent "should not make up any information or knowledge or procedures not provided by the user or the tools". The agent named the poem in each run and scored 1 in each.

The same task is in the public archive, and the same thing happens there: in 10 of its 16 runs the agent names the poem and its author, and 9 of those 10 received the full official reward. The reward checks the database and a list of required statements. It does not check everything the agent says.

Independent measurements put the gap between a passing score and a sound run in the same range. Cao et al. (2026) find that 31.1% of 3,420 runs succeed on the task while failing at least one harness criterion, and Jain and Sandhu (2026) find a user-specification violation in 24.4% of successful τ-bench episodes. Im (2026) reports that an LLM judge agreed with τ²-bench's native scoring on 56.2% of 2,160 episodes and passed at least 10 of the 11 episodes in which the agent made a forbidden write. From the optimizer's side, So, Liu and Long (2026) show the mechanism: an acceptance gate that scores task success sees what the harness does and not what it would still prevent.

**The simulated user is part of the measurement.** The fourth term of Equation (7.1) decided a whole batch. In the first four runs of a paired study designed to give both arms the same parent evidence, one customer was instructed to cancel two orders for two different reasons. The agent proposed one reason for both, and the simulated customer agreed without correction, so the database was written with a reason its own instructions contradict. Both reviewers confirmed the departure. Under the validity rule the run cannot serve as evidence for or against a strategy, and the batch ended there, at 4 of 120 planned episodes. That study measures the optimizer's downstream score with and without admission, and it is the next experiment.

### 8. Where the method sits and what it cost

The closest methods differ from ICFA in the unit they select, the evidence they use and what a selection costs.

**Table 5. The methods closest to ICFA.**

| Method | Selects | On the evidence of | Cost of one selection |
| --- | --- | --- | --- |
| GEPA (Agrawal et al., 2025) | Candidate prompts | Score on a minibatch, then a Pareto front | Rollouts |
| GEPA-Curator (Yu et al., 2026) | Tasks whose failures reach the optimizer | Signals that a failure is noise | Per task |
| AgentGrad (Chu et al., 2026) | The agent whose prompt to edit | A hint injected into one agent at a time, and the rerun | Reruns per failure |
| HarnessEvolve (Jiang et al., 2026) | Candidate harness edits | A quality gate and a performance gate on recent batches | Rollouts |
| STEVE (Xu et al., 2026) | Examples that produce a gradient; edits | Errors only; a preservation set | Rollouts |
| CAST (Saeidi et al., 2026) | Action-level rationales for training | The trajectory under partial observability | Training |
| **ICFA** | **Individual diagnoses, relative to the intervention** | **Execution records for origin; the action-time view for support** | **Zero model calls for integrity and origin; one judge call for evidence** |

Curating tasks removes whole episodes whose failure is noise; a single episode in this study carried a diagnosis that was noise and nothing else that was. Verifying by intervention establishes that an edit resolves a failure, which is stronger than reach and costs a rerun for every agent and failure; reach is the necessary condition for that test to succeed and can be checked before any rollout is spent. Candidate gates act after the edit is written. ICFA acts before, on the claim, and its acceptance rule adds to the candidate gates the conditions the score leaves out.

Table 6 gives the model calls that each measurement made and the tokens the model reported for them. The 18 development runs that the reviewer and the origin audit read made 248 calls of their own (Section 3), and the reference labels were assigned outside these counts.

**Table 6. Model calls and tokens of each measurement.**

| Measurement | Calls | Input tokens | Output tokens |
| --- | ---: | ---: | ---: |
| Reviewer on 18 runs | 18 | 284,840 | 6,894 |
| Evidence gate on 8 diagnoses | 8 | 130,049 | 4,315 |
| Evidence gate on 12 cards | 12 | 182,910 | 4,128 |
| Optimization, two arms | 240 | 3,589,164 | 27,027 |
| Final test, 18 completed runs and one interrupted | 273 | 3,689,217 | 21,717 |
| Paired batch, four runs | 61 | 893,326 | 9,586 |
| Integrity contract, 560 inputs | 0 | 0 | 0 |
| Origin: 181 messages, 36 initializations, 24,836 archived messages | 0 | 0 | 0 |

The two gates that cost nothing are the two that the transcript cannot replace: one says whether the score exists, the other says whose behavior it was. They are also the two that carry over unchanged to any agent system that keeps a ledger of its own calls.
