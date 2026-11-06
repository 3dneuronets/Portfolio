TITLE Low-voltage-activated calcium channel

COMMENT
    Low-voltage-activated (LVA) calcium channel.

    Note: mtau is an approximation from the published plots.

    References:
    Avery and Johnston (1996)
    tau from Randall (1997)

    The voltage dependence is shifted by -10 mV to correct for
    junction potential.

    Rates corrected using Q10 = 2.3,
    target temperature = 34 C,
    original temperature = 21 C.

    Mathematical formulation and physiological parameters are unchanged
    from the original mechanism.
ENDCOMMENT


NEURON {
    SUFFIX Ca_LVA
    USEION ca READ eca WRITE ica
    RANGE gbar, g, ica
}


UNITS {
    (S) = (siemens)
    (mV) = (millivolt)
    (mA) = (milliamp)
}


PARAMETER {
    gbar = 0.00001 (S/cm2)
}


ASSIGNED {
    v       (mV)
    eca     (mV)
    ica     (mA/cm2)
    g       (S/cm2)

    mInf
    mTau
    hInf
    hTau
}


STATE {
    m
    h
}


BREAKPOINT {
    SOLVE states METHOD cnexp

    g = gbar * m * m * h
    ica = g * (v - eca)
}


DERIVATIVE states {
    rates()

    m' = (mInf - m) / mTau
    h' = (hInf - h) / hTau
}


INITIAL {
    rates()

    m = mInf
    h = hInf
}


PROCEDURE rates() {
    LOCAL qt

    qt = 2.3^((34 - 21) / 10)

    UNITSOFF

        v = v + 10

        mInf = 1.0000 / (1 + exp((v - (-30.000)) / -6))
        mTau = (5.0000 + 20.0000 / (1 + exp((v - (-25.000)) / 5))) / qt

        hInf = 1.0000 / (1 + exp((v - (-80.000)) / 6.4))
        hTau = (20.0000 + 50.0000 / (1 + exp((v - (-40.000)) / 7))) / qt

        v = v - 10

    UNITSON
}