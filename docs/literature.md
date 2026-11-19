# Where this work sits

What must be true of a diagnosis before it is allowed to change an agent? Reflective optimizers supply the loop.
The literature on failure attribution and on LLM judges measures how reliable a diagnosis is. Work on benchmark
validity audits the instrument that produces the score. Methods for credit assignment and gating decide which
component to edit and which edit to keep. Each holds part of the answer. This page records what each line
establishes, where it stops, and what the article adds. The complete list of 111 sources is in the
[bibliography](bibliography.md).

## The short version

| Line of work | What it establishes | Where it stops | What the article adds |
| --- | --- | --- | --- |
| Reflective optimization: GEPA, TextGrad, ProTeGi, DSPy | Natural-language diagnoses of failed traces are an efficient learning signal for prompts | The diagnosis is taken as given | An admission step in front of the optimizer, with a named exit for every refusal |
| Feedback selection and credit assignment: GEPA-Curator, AgentGrad, CANTANTE, MAPRO | Noisy tasks should be kept from the optimizer; the prompt to edit can be identified by intervention or by contrasting rollouts | The unit is a task or an editable prompt; a rerun is the evidence | A relation between one diagnosis and the intervention, decided from execution records before any rerun |
| Candidate gating: HarnessEvolve, STEVE, Masked Erosion | Edits need a regression check; a gate on task success misses what the score does not show | Gates act on the candidate, after the edit is written | Admission before the edit, and an acceptance rule with terms the score leaves out |
| Failure attribution and judges: Who&When, Shen et al., Counsel, AgentRewardBench | Automated attribution is weak, and a judge's "first mistake" often does not mark a cause | The transcript is the judge's only input | A proof that the producer cannot be read from the transcript, and a gate that reads the ledger |
| Benchmark instruments: ABC, Liu, Xia et al., Bellibatlu et al., Im | Graders, renderers and logs fail silently and change scores | Audits of whole benchmarks and leaderboards | A contract at the narrowest point, one judge reply and one score, and a census of message origin on a public archive |
| Simulated users: UserProxyBench, Tennenholtz et al. | The user proxy changes the reward and often departs from its instructions | Measured as a property of the benchmark | User validity as a term of acceptance |
| Causation and responsibility: Pearl, Woodward, Halpern and Pearl, Chockler and Halpern | Cause is what an intervention can change; responsibility is graded | Stated for general causal models | Reach as the necessary condition for an optimizer's edit, with a zero-cost test |

## Timing

The experiments ran from May to September 2026. τ-bench, τ²-bench, GEPA, the Who&When dataset, the Agentic
Benchmark Checklist and CANTANTE precede them or appeared as they began. CAST, HarnessEvolve and AgentGrad were
posted in their last three weeks. GEPA-Curator, UserProxyBench, the prefix-value study of Shen et al., the
leaderboard audit of Liu, the evaluator study of Im and the input-assurance study of Xia et al. followed between
late September and November. Several of the later papers measure, on other data, effects this study met on its
own: a simulated user that departs from its instructions, a passing score on an unsound run, and stored actions
whose label does not say who wrote them.

## Key sources

### Reflective optimization

**Agrawal et al. (2025), "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning."** [arXiv](https://arxiv.org/abs/2507.19457)
GEPA samples trajectories, reflects on them in natural language to diagnose problems, proposes and tests prompt
edits and combines lessons from a Pareto front of candidates; it outperforms GRPO by 6% on average with up to 35
times fewer rollouts and the MIPROv2 optimizer by over 10%. It is the optimizer of this study. Its sample
efficiency comes from trusting each reflection, which is the reason to examine what the reflection is given.

**Yuksekgonul et al. (2024), "TextGrad: Automatic 'Differentiation' via Text."** [arXiv](https://arxiv.org/abs/2406.07496)
Textual feedback from a language model is propagated backward through a computation graph to improve its
components. The graph is the right object: it is the same graph on which reach is defined. TextGrad's variables
are the nodes one chooses to optimize; a component outside that set, such as a framework constant, has no
gradient and can still be blamed in the text.

**Pryzant et al. (2023), "Automatic Prompt Optimization with 'Gradient Descent' and Beam Search."** [arXiv](https://arxiv.org/abs/2305.03495)
The original statement of the idea: natural-language "gradients" that criticize the current prompt on a
minibatch, applied by editing the prompt in the opposite semantic direction. The criticism is produced and
consumed by the same loop with no check between.

**Zhou and Cheng (2026), "What Should the Reflector See?"** [arXiv](https://arxiv.org/abs/2609.32452)
Nine reflection strategies on five datasets: showing failures only gives the largest mean test gain, and the
strategy that best improves the sampled parent yields little final gain. The study varies which examples the
reflector sees. The validity of the diagnosis attached to an example is held fixed, and that is the variable
admission controls.

**Lumer et al. (2026), "Reflective Prompt Optimization of a Deep-Research Agent."** [arXiv](https://arxiv.org/abs/2610.12601)
Under a topic-disjoint split, GEPA raises held-out citation reward from 0.702 to 0.781, and an ablation
identifies decomposed per-dimension feedback as the causal ingredient: collapsed to one scalar, held-out transfer
turns negative. The content of the feedback decides whether the gain transfers, which is evidence for treating
feedback as something to be qualified.

### Selecting feedback and assigning credit

**Yu et al. (2026), "GEPA-Curator: Curated Learning for Self Improving Agents."** [arXiv](https://arxiv.org/abs/2610.37651)
The closest method. Its premise is the same as this study's: agentic failures can come from prompt weaknesses,
harness limitations, stochastic execution or noisy judges, and such failures may be harmful as learning signal.
It filters out tasks likely to give unreliable signal and retrieves prior successes, with gains of up to 20.7%
over GEPA. The unit is the task. A task can be sound and carry one diagnosis addressed to the wrong component,
which task curation keeps and admission routes.

**Chu et al. (2026), "AgentGrad: Intervention-guided Prompt Optimization for Multi-Agent Systems."** [arXiv](https://arxiv.org/abs/2609.08572)
For each failure a hint is injected into one agent at a time to identify the agent whose modification resolves
it, and that agent's corrected output supervises the gradient. This verifies that an edit works, which is
stronger than reach. It needs a rerun per agent and failure, and its candidates are agents' prompts, so a
behavior produced by none of them is outside its search. Reach is the necessary condition for its test to
succeed and costs no rollout.

**Zehle (2026), "CANTANTE."** [arXiv](https://arxiv.org/abs/2605.13295) **Z. Zhang et al. (2025), "MAPRO."** [arXiv](https://arxiv.org/abs/2510.07475)
Both treat multi-agent prompt optimization as credit assignment: CANTANTE decomposes a system-level reward into
per-agent signals by contrasting rollouts of joint configurations on the same query, and MAPRO casts the problem
as maximum a posteriori inference. Credit is divided among the editable prompts. Whether the behavior belongs to
an editable component is assumed.

**Jiang et al. (2026), "HarnessEvolve."** [arXiv](https://arxiv.org/abs/2609.00829)
Failed executions are aligned against reference trajectories produced with the ground-truth answer, and candidate
harness edits must pass a quality gate against leakage and bloat and a performance gate against degradation.
Because it edits prompts, tools and code, its reach is the whole harness, the top of the routing lattice in
Section 2. Its diagnosis uses the reference answer; the evidence gate here withholds it, on the ground that the
agent did not have it.

**Saeidi et al. (2026), "CAST: Critique-Aware Supervision for Training Reliable Long-Horizon Tool-Calling Agents."** [arXiv](https://arxiv.org/abs/2608.30147)
Sparse task outcomes are converted into action-level rationales explaining action validity under partial
observability, and the critique model supplies training data for the policy. The action-time view of Section 5
follows the same principle. CAST produces critiques; this work decides which existing critiques may be used, and
adds the question of who performed the action.

**So, Liu and Long (2026), "Masked Erosion."** [arXiv](https://arxiv.org/abs/2610.38392)
An acceptance gate that scores task success sees what the harness does under the current model and not what it
would still prevent, so redundant safeguards are deleted unseen; GEPA kept every safety rule verbatim and two of
its three final harnesses misused credentials under a weaker model. The paper establishes from the optimizer's
side what Section 7 finds from the evaluator's: the score is not the acceptance criterion.

### Diagnoses and judges

**S. Zhang et al. (2025), "Which Agent Causes Task Failures and When?"** [arXiv](https://arxiv.org/abs/2505.00212)
The Who&When dataset annotates failure logs from 127 multi-agent systems with the responsible agent and the
decisive step. The best method reaches 53.5% on the agent and 14.2% on the step. The annotation scheme assumes
that every failure has a responsible agent among the agents; a failure produced by the framework has no correct
label in it.

**Shen et al. (2026), "Executable Prefix Values for Locating Agent Failures."** [arXiv](https://arxiv.org/abs/2610.17633)
Agents are restarted from intermediate states of failed trajectories to estimate the probability of success from
each step. For 66% of the steps judges label as the first mistake, that probability does not drop at the step,
and judges of different lineages agree on the exact step in 21 of 57 cases. A label is a claim, and a claim can
be tested by execution. The test they use is a restart; the test in Section 3 is cheaper because the question,
whether the prompt can reach the message, is narrower.

**Pisupati et al. (2026), "Counsel: A Meta-Evaluation Dataset for Agentic Tasks."** [arXiv](https://arxiv.org/abs/2606.21627)
Human annotators grade the critiques that open-weight judges write on τ-bench and DA-Code trajectories as "spot
on", "correct location but poor reasoning" or "should not have flagged", with a Krippendorff's alpha of 0.78. It
is the labelled resource the evidence gate needs for calibration, on the same benchmark family.

**Lù et al. (2025), "AgentRewardBench."** [arXiv](https://arxiv.org/abs/2504.08942)
1,302 web-agent trajectories reviewed by experts, against which twelve LLM judges are evaluated; no single judge
excels across benchmarks. The paper measures the judge as an evaluator of outcomes. The gate here uses a judge on
a narrower question with a narrower input, and reports its errors by tier.

### Benchmark instruments

**Yao et al. (2024), "τ-bench"; Barres et al. (2025), "τ²-Bench."** [arXiv](https://arxiv.org/abs/2406.12045) · [arXiv](https://arxiv.org/abs/2506.07982)
The benchmark family of this study: a simulated user, domain tools, a policy, and evaluation by the final
database state, with the pass^k metric for reliability over repeated trials. τ²-bench adds a dual-control telecom
domain and a user simulator coupled to the environment. The framework is carefully built and publicly archived,
which is what makes the census of Section 3 possible.

**Zhu et al. (2025), "Establishing Best Practices for Building Rigorous Agentic Benchmarks."** [arXiv](https://arxiv.org/abs/2507.02825)
A checklist distilled from issues in existing benchmarks, among them that τ-bench counted empty responses as
successful; such issues move measured performance by up to 100% in relative terms. The integrity contract is one
item of that checklist made executable for one evaluator.

**Liu (2026), "Silent Instrument Errors Reorder Agent Leaderboards."** [arXiv](https://arxiv.org/abs/2611.04399)
From published artifacts alone, an audit of HAL and τ²-bench finds ungraded episodes stored as failures, a cost
column that double counts, and archived trajectories that store grader-written actions as agent actions; it
recommends tagging the origin of every stored action. The audit is independent of this study and reaches the
same instrument from the leaderboard's side. The article adds the count for one kind of non-agent message and a
decision rule that uses the tag.

**Xia et al. (2026), "Does the Judge See What the Evaluation Requires?"** [arXiv](https://arxiv.org/abs/2611.02676)
Four input-assurance obligations for judge pipelines, and a pipeline in which a renderer omitted every structured
tool call, leaving 53 of 60 judged steps blank while hashes matched. Their obligations cover the path from record
to judge; Equation (4.1) covers the path from judge to score.

**Im (2026), "When Evaluators of AI Agents Disagree."** [arXiv](https://arxiv.org/abs/2611.14581)
On 2,160 τ²-bench episodes a judge agreed with native scoring on 56.2%, and a rule-based check of whether a write
was expected caught all 11 forbidden writes that the judge mostly passed. The finding that a deterministic check
on the record outperforms a judge on the question it can answer is the design principle of gates 1 and 2.

**Cao et al. (2026), "Trial by Trace."** [arXiv](https://arxiv.org/abs/2610.32285)
A benchmark of agent harnesses on seven reliability components, with trajectory tracing and failure attribution
through explicit mechanism chains; 31.1% of 3,420 runs succeed on the task while failing at least one harness
criterion. The figure is the same gap as qualified against official passes in Section 7.

### Simulated users

**Jain and Sandhu (2026), "UserProxyBench."** [arXiv](https://arxiv.org/abs/2609.38043)
With the agent fixed, varying the user proxy across 375 tasks of the τ-bench family changes mean reward by 15.2
points, and 24.4% of successful episodes contain a user-specification violation. The simulated user is an
uncontrolled instrument. The acceptance rule makes its validity a condition.

**Tennenholtz et al. (2026), "Controllable User Simulation."** [arXiv](https://arxiv.org/abs/2605.11519)
Controllable simulation is formalized as a causal inference problem, and training a simulator on post-hoc
trajectory labels is shown to inject a look-ahead bias. The hindsight that the evidence gate removes from
diagnoses has a counterpart inside the user simulator.

### Causation, responsibility and hindsight

**Pearl (2009), *Causality*; Woodward (2003), *Making Things Happen*.** [doi](https://doi.org/10.1017/CBO9780511803161) · [doi](https://doi.org/10.1093/0195155270.001.0001)
A cause is a variable whose manipulation changes the effect. Equation (2.2) is this definition applied to one
question: can a manipulation of the prompt change this message.

**Halpern and Pearl (2005); Chockler and Halpern (2004).** [doi](https://doi.org/10.1093/bjps/axi147) · [doi](https://doi.org/10.1613/jair.1391)
Actual causation in structural models, and responsibility and blame as graded notions built on it. A full
attribution would compute them. Reach is the coarse precondition, and it is the part an optimizer needs first.

**Peters, Bühlmann and Meinshausen (2016), "Causal Inference by Using Invariant Prediction."** [doi](https://doi.org/10.1111/rssb.12167)
Causal predictors are those whose relation to the target is invariant across environments. The initialization
control and the archive use invariance in the other direction, to show what the prompt does not cause.

**Sawarni et al. (2026), "Knowing When to Intervene."** [arXiv](https://arxiv.org/abs/2611.09792)
A framework for estimating the causal effect of interventions inside agent trajectories from randomized
interventions, applied to τ-bench retail among others; effects vary substantially across actions and states. It
estimates how much an intervention helps where it can act. Reach says where it can act.

**Fischhoff (1975); Baron and Hershey (1988).** [doi](https://doi.org/10.1037/0096-1523.1.3.288) · [doi](https://doi.org/10.1037/0022-3514.54.4.569)
Knowing an outcome raises its judged foreseeability, and decisions are graded by their outcomes. A reviewer that
reads the task's reference is in the position of their subjects.

### Contracts and exact statistics

**Meyer (1992), "Applying 'Design by Contract'"; Saltzer and Schroeder (1975).** [doi](https://doi.org/10.1109/2.161279) · [doi](https://doi.org/10.1109/PROC.1975.9939)
Obligations stated as preconditions and postconditions, and the principle of fail-safe defaults: base decisions
on permission, not exclusion. Equation (4.1) is a postcondition on a judge's reply with a fail-safe default of
unknown.

**Altman and Bland (1994); Chow (1970); Clopper and Pearson (1934).** [doi](https://doi.org/10.1136/bmj.309.6947.102) · [doi](https://doi.org/10.1109/TIT.1970.1054406) · [doi](https://doi.org/10.1093/biomet/26.4.404)
Predictive values depend on prevalence; a classifier with a reject option trades error against rejection; exact
binomial limits. Equation (6.1), the abstain outcome and the clean-run bounds are these three results in use.
