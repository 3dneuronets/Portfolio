TITLE AMPA and NMDA receptor with probabilistic presynaptic short-term plasticity

COMMENT
CoreNEURON 9.0.1 GPU-compatible port of ProbAMPANMDA.

Important implementation details:
  * native NMODL RANDOM stream; no POINTER or VERBATIM RNG plumbing
  * no nested INITIAL block inside NET_RECEIVE
  * per-NetCon plasticity state is initialized lazily on the first event
  * Pv_tmp and Pr are event-local temporaries, not persistent NetCon weights
  * random_negexp(rng) preserves the effective distribution used by the
    original mechanism (Random.negexp(1) / exprand(1))
  * mg and mggate are per-instance values

The original NONSPECIFIC_CURRENT declaration is retained exactly. Because
'i' is also the sum of i_AMPA and i_NMDA, this preserves the original model's
current accounting, including its apparent double counting of component
currents.
ENDCOMMENT

NEURON {
    POINT_PROCESS ProbAMPANMDA

    RANGE tau_r_AMPA, tau_d_AMPA, tau_r_NMDA, tau_d_NMDA
    RANGE Use, Dep, Fac, u0, weight_factor_NMDA
    RANGE i, i_AMPA, i_NMDA, g_AMPA, g_NMDA
    RANGE e, gmax, mg, mggate

    NONSPECIFIC_CURRENT i, i_AMPA, i_NMDA

    RANDOM rng
    THREADSAFE
}

PARAMETER {
    tau_r_AMPA = 0.2  (ms)
    tau_d_AMPA = 1.7  (ms)
    tau_r_NMDA = 0.29 (ms)
    tau_d_NMDA = 43   (ms)

    Use = 1.0 (1)
    Dep = 100 (ms)
    Fac = 10  (ms)
    u0  = 0   (1)

    e  = 0 (mV)
    mg = 1 (mM)

    gmax = 0.001 (uS)
    weight_factor_NMDA = 1 (1)
}

ASSIGNED {
    v (mV)

    i      (nA)
    i_AMPA (nA)
    i_NMDA (nA)

    g_AMPA (uS)
    g_NMDA (uS)

    mggate (1)
    factor_AMPA (1)
    factor_NMDA (1)
}

STATE {
    A_AMPA
    B_AMPA
    A_NMDA
    B_NMDA
}

INITIAL {
    LOCAL tp_AMPA, tp_NMDA

    A_AMPA = 0
    B_AMPA = 0
    A_NMDA = 0
    B_NMDA = 0

    tp_AMPA = (tau_r_AMPA * tau_d_AMPA) / (tau_d_AMPA - tau_r_AMPA) * log(tau_d_AMPA / tau_r_AMPA)
    factor_AMPA = 1 / (-exp(-tp_AMPA / tau_r_AMPA) + exp(-tp_AMPA / tau_d_AMPA))

    tp_NMDA = (tau_r_NMDA * tau_d_NMDA) / (tau_d_NMDA - tau_r_NMDA) * log(tau_d_NMDA / tau_r_NMDA)
    factor_NMDA = 1 / (-exp(-tp_NMDA / tau_r_NMDA) + exp(-tp_NMDA / tau_d_NMDA))

    : Keep configured Random123 IDs, but restart the sequence at finitialize().
    random_setseq(rng, 0)
}

BREAKPOINT {
    SOLVE state METHOD cnexp

    mggate = 1 / (1 + exp(-0.062 (/mV) * v) * (mg / 3.57 (mM)))

    g_AMPA = gmax * (B_AMPA - A_AMPA)
    g_NMDA = gmax * (B_NMDA - A_NMDA) * mggate

    i_AMPA = g_AMPA * (v - e)
    i_NMDA = g_NMDA * (v - e)
    i = i_AMPA + i_NMDA
}

DERIVATIVE state {
    A_AMPA' = -A_AMPA / tau_r_AMPA
    B_AMPA' = -B_AMPA / tau_d_AMPA
    A_NMDA' = -A_NMDA / tau_r_NMDA
    B_NMDA' = -B_NMDA / tau_d_NMDA
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

        A_AMPA = A_AMPA + weight * factor_AMPA
        B_AMPA = B_AMPA + weight * factor_AMPA

        A_NMDA = A_NMDA + weight * weight_factor_NMDA * factor_NMDA
        B_NMDA = B_NMDA + weight * weight_factor_NMDA * factor_NMDA
    }
}
