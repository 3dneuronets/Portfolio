TITLE Dual-exponential inhibitory synapse with probabilistic short-term plasticity

COMMENT
CoreNEURON 9.0.1 GPU-compatible port of ProbUDFsyn.

Important implementation details:
  * native NMODL RANDOM stream; no POINTER or VERBATIM RNG plumbing
  * no nested INITIAL block inside NET_RECEIVE
  * per-NetCon plasticity state is initialized lazily on the first event
  * Pv_tmp and Pr are event-local temporaries, not persistent NetCon weights
  * random_negexp(rng) preserves the effective distribution used by the
    original mechanism (Random.negexp(1) / exprand(1))
ENDCOMMENT

NEURON {
    POINT_PROCESS ProbUDFsyn

    RANGE tau_r, tau_d
    RANGE Use, Dep, Fac, u0
    RANGE i, g, e, gmax

    NONSPECIFIC_CURRENT i

    RANDOM rng
    THREADSAFE
}

PARAMETER {
    tau_r = 0.2 (ms)
    tau_d = 1.7 (ms)

    Use = 1.0 (1)
    Dep = 100 (ms)
    Fac = 10  (ms)
    u0  = 0   (1)

    e = 0 (mV)
    gmax = 0.001 (uS)
}

ASSIGNED {
    v (mV)
    i (nA)
    g (uS)
    factor (1)
}

STATE {
    A
    B
}

INITIAL {
    LOCAL tp

    A = 0
    B = 0

    tp = (tau_r * tau_d) / (tau_d - tau_r) * log(tau_d / tau_r)
    factor = 1 / (-exp(-tp / tau_r) + exp(-tp / tau_d))

    : Keep configured Random123 IDs, but restart the sequence at finitialize().
    random_setseq(rng, 0)
}

BREAKPOINT {
    SOLVE state METHOD cnexp

    g = gmax * (B - A)
    i = g * (v - e)
}

DERIVATIVE state {
    A' = -A / tau_r
    B' = -B / tau_d
}

NET_RECEIVE (weight, Pv, u, tsyn (ms), initialized) {
    LOCAL Pv_tmp, Pr

    : With no NET_RECEIVE INITIAL block, NEURON resets all weight slots after
    : weight[0] to zero at finitialize().  Initialize this NetCon's STP state
    : when its first event is delivered.  The original nested INITIAL block
    : ran at t=0, hence tsyn starts at 0 here as well.
    if (initialized == 0) {
        Pv = 1
        u = u0
        tsyn = 0
        initialized = 1
    }

    : Facilitation (Fuhrmann et al., Eq. 2).
    if (Fac > 0) {
        u = u * exp(-(t - tsyn) / Fac)
        u = u + Use * (1 - u)
    } else {
        u = Use
    }

    : Vesicle availability and release probability (Eq. 3).
    Pv_tmp = 1 - (1 - Pv) * exp(-(t - tsyn) / Dep)
    Pr = u * Pv_tmp
    Pv_tmp = Pv_tmp - u * Pv_tmp

    : Preserve the original mechanism's negative-exponential random draw.
    if (random_negexp(rng) < Pr) {
        tsyn = t
        Pv = Pv_tmp

        A = A + weight * factor
        B = B + weight * factor
    }
}
