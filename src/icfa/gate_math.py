"""The arithmetic of admission: what a gate does to the feedback that passes it.

Notation. p is the share of valid diagnoses among those offered to a gate, t
the share of valid ones it admits and f the share of invalid ones it admits.
Standard library only.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb


def precision(p, t, f):
    """Share of admitted diagnoses that are valid: pt / (pt + (1 - p) f)."""
    admitted = p * t + (1 - p) * f
    if admitted == 0:
        raise ValueError("nothing is admitted")
    return p * t / admitted


def admitted_share(p, t, f):
    """Share of offered diagnoses that pass: pt + (1 - p) f."""
    return p * t + (1 - p) * f


def odds(p, t, f):
    """Posterior odds of validity: the prior odds multiplied by t / f."""
    if p == 1 or f == 0:
        raise ValueError("odds are unbounded")
    return (p / (1 - p)) * (t / f)


def improves(t, f):
    """A gate raises precision exactly when it admits valid diagnoses more readily than invalid ones."""
    return t > f


def chain(gates):
    """Gates in series, deciding independently given validity: rates multiply."""
    t = f = 1
    for gate_t, gate_f in gates:
        t, f = t * gate_t, f * gate_f
    return t, f


def false_admission(class_shares, class_rates):
    """False-admission rate over invalid classes k with shares w_k and rates f_k: sum of w_k f_k."""
    if len(class_shares) != len(class_rates) or sum(class_shares) != 1:
        raise ValueError("class shares must sum to one and match the rates")
    return sum(w * f for w, f in zip(class_shares, class_rates))


def net_benefit(p, t, f, value, harm, cost=0):
    """Gain per offered diagnosis from running the gate.

    A valid admitted diagnosis is worth ``value`` and an invalid admitted one
    costs ``harm``; running the gate costs ``cost`` per diagnosis. The gate
    pays when the harm it removes exceeds the value it removes plus its cost:
    (1 - p)(1 - f) harm - p (1 - t) value - cost > 0.
    """
    return (1 - p) * (1 - f) * harm - p * (1 - t) * value - cost


def break_even_diagnoses(gate_cost, wasted_candidate_cost):
    """How many diagnoses a gate may screen per wasted candidate it prevents and still break even."""
    return wasted_candidate_cost / gate_cost


def transcript_only_error_floor(q):
    """Least error of any gate that reads only the transcript, on two runs with one
    transcript and different producers occurring with probabilities q and 1 - q."""
    return min(q, 1 - q)


def clean_run_upper_bound(n, confidence=0.95):
    """Exact one-sided upper bound on a rate after n trials with no event: 1 - (1 - confidence)^(1/n)."""
    if n <= 0:
        raise ValueError("n must be positive")
    return 1 - (1 - confidence) ** (1 / n)


def binomial_tail_at_most(k, n, rate):
    """P(X <= k) for X ~ Binomial(n, rate)."""
    return sum(comb(n, i) * rate ** i * (1 - rate) ** (n - i) for i in range(k + 1))


def clopper_pearson_upper(k, n, confidence=0.95):
    """Exact one-sided upper confidence bound for a binomial rate (Clopper and Pearson 1934)."""
    if not 0 <= k <= n or n <= 0:
        raise ValueError("need 0 <= k <= n and n > 0")
    if k == n:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(200):
        mid = (low + high) / 2
        if binomial_tail_at_most(k, n, mid) > 1 - confidence:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def exact(numerator, denominator):
    """A count ratio as an exact fraction, for tables that must not round twice."""
    return Fraction(numerator, denominator)
