TITLE Tonic GABA current with rectification

NEURON {
    SUFFIX tonic
    NONSPECIFIC_CURRENT i
    RANGE i, a, b, g, e_gaba
}

PARAMETER {
    g = 0.001 (S/cm2)
    e_gaba = -80 (mV)
}

ASSIGNED {
    v (mV)
    i (mA/cm2)
    a (/ms)
    b (/ms)
}

STATE {
    o
    c
}

BREAKPOINT {
    SOLVE kin METHOD sparse
    i = g * o * (v - e_gaba)
}

INITIAL {
    SOLVE kin STEADYSTATE sparse
}

KINETIC kin {
    rates(v)

    ~ o <-> c (b, a)

    CONSERVE o + c = 1
}

PROCEDURE rates(v (mV)) {
    LOCAL x, y

    UNITSOFF

    x = 0.1 * (v + 20)

    if (fabs(x) > 1e-6) {
        a = (50 * x) / (1 - exp(-x))
    } else {
        a = 0.25 * (v^2 + 20 * v + 200)
    }

    y = -0.08 * (v - 10)

    if (fabs(y) > 1e-6) {
        b = (20 * y) / (1 - exp(-y))
    } else {
        b = -0.064 * (v^2 - 45 * v + 37.5)
    }

    UNITSON
}