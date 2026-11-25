TITLE Fluctuating conductances with a native Random123 stream

COMMENT
CoreNEURON 9.0.1-compatible Gfluct2 implementation.

The Random123 stream is declared with RANDOM rng. Its identifiers are assigned
from Python through the NMODLRandom wrapper:

    ou.rng.set_ids(id1, id2, id3)
    ou.rng.set_seq(0)

Do not call random_setids() in this MOD file with CoreNEURON 9.0.1: that
version's CoreNEURON translation can emit a call to an unavailable
nrnran123_setids symbol. Also use random_normal(rng), without mean/std
arguments, because the generated CoreNEURON helper accepts only the stream.
ENDCOMMENT

NEURON {
    POINT_PROCESS Gfluct2
    NONSPECIFIC_CURRENT i

    RANGE E_e, E_i
    RANGE g_e0, g_i0, std_e, std_i, tau_e, tau_i
    RANGE g_e, g_i, g_e1, g_i1, D_e, D_i

    RANDOM rng
    THREADSAFE
}

UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (umho) = (micromho)
}

PARAMETER {
    dt              (ms)

    E_e   = 0        (mV)
    E_i   = -75      (mV)

    g_e0  = 0.0121   (umho)
    g_i0  = 0.0573   (umho)

    std_e = 0.0030   (umho)
    std_i = 0.0066   (umho)

    tau_e = 2.728    (ms)
    tau_i = 10.49    (ms)
}

ASSIGNED {
    v       (mV)
    i       (nA)

    g_e     (umho)
    g_i     (umho)
    g_e1    (umho)
    g_i1    (umho)

    D_e     (umho umho/ms)
    D_i     (umho umho/ms)

    exp_e
    exp_i
    amp_e   (umho)
    amp_i   (umho)
}

INITIAL {
    : IDs are set from Python before finitialize/CoreNEURON transfer.
    : Reset the counter on every initialization.
    random_setseq(rng, 0)

    g_e1 = 0
    g_i1 = 0
    g_e  = g_e0
    g_i  = g_i0

    D_e   = 0
    D_i   = 0
    exp_e = 0
    exp_i = 0
    amp_e = 0
    amp_i = 0

    if (tau_e > 0) {
        D_e   = 2 * std_e * std_e / tau_e
        exp_e = exp(-dt/tau_e)
        amp_e = std_e * sqrt(1 - exp(-2*dt/tau_e))
    }

    if (tau_i > 0) {
        D_i   = 2 * std_i * std_i / tau_i
        exp_i = exp(-dt/tau_i)
        amp_i = std_i * sqrt(1 - exp(-2*dt/tau_i))
    }
}

BREAKPOINT {
    SOLVE oup

    g_e = g_e0 + g_e1
    if (g_e < 0) {
        g_e = 0
    }

    g_i = g_i0 + g_i1
    if (g_i < 0) {
        g_i = 0
    }

    i = g_e * (v - E_e) + g_i * (v - E_i)
}

PROCEDURE oup() {
    if (tau_e > 0) {
        g_e1 = exp_e * g_e1 + amp_e * random_normal(rng)
    } else {
        g_e1 = std_e * random_normal(rng)
    }

    if (tau_i > 0) {
        g_i1 = exp_i * g_i1 + amp_i * random_normal(rng)
    } else {
        g_i1 = std_i * random_normal(rng)
    }
}
