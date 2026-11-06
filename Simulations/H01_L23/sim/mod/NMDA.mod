TITLE NMDA receptor with voltage-dependent Mg2+ block

COMMENT
NMDA receptor conductance with a dual-exponential kinetic profile.


The synaptic conductance is described by the difference between
two state variables with rise and decay time constants.

The NMDA receptor includes a voltage-dependent Mg2+ block
following the formulation of Jahr and Stevens (1990).

The original kinetic parameters and mathematical formulation
are preserved from the original mechanism.

No presynaptic short-term plasticity is implemented in this mechanism.


ENDCOMMENT

NEURON {
POINT_PROCESS NMDA


RANGE tau_r_NMDA
RANGE tau_d_NMDA
RANGE n_NMDA
RANGE gama_NMDA

RANGE i
RANGE i_NMDA
RANGE g_NMDA
RANGE e

NONSPECIFIC_CURRENT i


}

UNITS {
(mV) = (millivolt)
(nA) = (nanoamp)
(uS) = (microsiemens)
}

PARAMETER {
tau_r_NMDA = 0.3 (ms)
tau_d_NMDA = 43 (ms)


n_NMDA = 0.28011 (/mM)
gama_NMDA = 0.062 (/mV)

e = 0 (mV)

mg = 1 (mM)


}

ASSIGNED {
v (mV)


i (nA)
i_NMDA (nA)

g_NMDA (uS)

factor_NMDA
mggate

tp_NMDA (ms)


}

STATE {
A_NMDA (uS)
B_NMDA (uS)
}

INITIAL {
A_NMDA = 0
B_NMDA = 0


tp_NMDA = (tau_r_NMDA * tau_d_NMDA) /
          (tau_d_NMDA - tau_r_NMDA) *
          log(tau_d_NMDA / tau_r_NMDA)

factor_NMDA =
    1 / (
        -exp(-tp_NMDA / tau_r_NMDA) +
         exp(-tp_NMDA / tau_d_NMDA)
    )


}

BREAKPOINT {
SOLVE state METHOD cnexp


mggate =
    1 / (
        1 +
        exp(gama_NMDA * (-v)) *
        (mg / 3.57)
    )

g_NMDA =
    (B_NMDA - A_NMDA) * mggate

i_NMDA =
    g_NMDA * (v - e)

i =
    i_NMDA


}

DERIVATIVE state {
A_NMDA' =
-A_NMDA / tau_r_NMDA


B_NMDA' =
    -B_NMDA / tau_d_NMDA


}

NET_RECEIVE(weight (uS)) {
A_NMDA =
A_NMDA +
weight * factor_NMDA


B_NMDA =
    B_NMDA +
    weight * factor_NMDA


}
