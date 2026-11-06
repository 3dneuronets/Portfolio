TITLE Persistent potassium current

COMMENT
    The persistent component of the potassium current.

    Reference:
    Voltage-gated K+ channels in layer 5 neocortical pyramidal
    neurones from young rats: subtypes and gradients,
    Korngreen and Sakmann, J. Physiology, 2000.

    Voltage shifted by -10 mV to correct for junction potential.

    Rates corrected using Q10 = 2.3,
    target temperature = 34 C,
    original temperature = 21 C.
ENDCOMMENT

NEURON {
    SUFFIX K_P
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
    ik = g * (v - ek)
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

    : Apply the original +10 mV voltage shift
    : using a local variable, without modifying v itself.


    UNITSOFF
        v = v + 10
        mInf = 1 / (1 + exp(-(v + 1) / 12))

        if (v < -50) {
            mTau = (1.25 + 175.03 * exp(-0.026 * -v)) / qt
        } else {
            mTau = (1.25 + 13 * exp(-v*0.026)) / qt
        }

        hInf = 1 / (1 + exp(-(v + 54) / (-11)))

        hTau = (360 + (1010 + 24 * (v + 55)) * exp(-((v + 75) / 48)^2)) / qt
        v = v - 10
    UNITSON
}