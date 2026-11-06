TITLE M-type potassium current

COMMENT
    M-current and other potassium currents in bullfrog sympathetic neurones.

    Reference:
    Adams et al. 1982 - M-currents and other potassium currents
    in bullfrog sympathetic neurones.

    Rates corrected using Q10 = 2.3,
    target temperature = 34 C,
    original temperature = 21 C.
ENDCOMMENT

NEURON {
    SUFFIX Im
    USEION k READ ek WRITE ik
    RANGE gbar, g, ik
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
    ek      (mV)
    ik      (mA/cm2)
    g       (S/cm2)

    mInf
    mTau
    mAlpha
    mBeta
}

STATE {
    m
}

BREAKPOINT {
    SOLVE states METHOD cnexp

    g = gbar * m
    ik = g * (v - ek)
}

DERIVATIVE states {
    rates()

    m' = (mInf - m) / mTau
}

INITIAL {
    rates()

    m = mInf
}

PROCEDURE rates() {
    LOCAL qt

    qt = 2.3^((34 - 21) / 10)

    UNITSOFF

        mAlpha = 3.3e-3 * exp(2.5 * 0.04 * (v - (-35)))
        mBeta  = 3.3e-3 * exp(-2.5 * 0.04 * (v - (-35)))

        mInf = mAlpha / (mAlpha + mBeta)

        mTau = (1 / (mAlpha + mBeta)) / qt

    UNITSON
}