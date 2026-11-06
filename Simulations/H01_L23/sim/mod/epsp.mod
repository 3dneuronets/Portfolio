TITLE EPSP-like exponential rise and decay current

COMMENT
    Exponential rise and decay current.

    Schaefer et al. (2003)

    Modified from syn2.mod.

    The current is defined as:

        i = 0, for t < onset

        i = -amp * [
                (1 - exp(-(t-onset)/tau0))
                - (1 - exp(-(t-onset)/tau1))
            ]

    for t >= onset.

    The amplitude is normalized so that the peak current is equal
    to imax.

    Mathematical formulation and physiological parameters are
    unchanged from the original mechanism.
ENDCOMMENT


INDEPENDENT {
    t FROM 0 TO 1 WITH 1 (ms)
}


NEURON {
    POINT_PROCESS epsp
    RANGE onset, tau0, tau1, imax, i, myv
    NONSPECIFIC_CURRENT i
}


UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (umho) = (micromho)
}


PARAMETER {
    onset = 0 (ms)
    tau0 = 0.2 (ms)
    tau1 = 3.0 (ms)
    imax = 0 (nA)

    v (mV)
}


ASSIGNED {
    i (nA)
    myv (mV)
}


BREAKPOINT {
    myv = v
    i = curr(t)
}


FUNCTION myexp(x) {
    if (x < -100) {
        myexp = 0
    } else {
        myexp = exp(x)
    }
}


FUNCTION curr(x) {
    LOCAL   tpeak, adjust, amp

    tpeak = tau0 * tau1 * log(tau0 / tau1) / (tau0 - tau1)

    adjust = 1 / ((1 - myexp(-tpeak / tau0)) - (1 - myexp(-tpeak / tau1)))

    amp = adjust * imax

    if (x < onset) {
        curr = 0
    } else {
        curr = -amp * ((1 - myexp(-(x - onset) / tau0))- (1 - myexp(-(x - onset) / tau1))
        )
    }
}