#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <errno.h>  
#include <time.h>

#define IA 16807
#define IM 2147483647
#define AM (1.0 / IM)
#define IQ 127773
#define IR 2836
#define NTAB 32
#define NDIV (1 + (IM - 1) / NTAB)
#define EPS 1.2e-7
#define RNMX (1.0 - EPS)
#define PI acos(-1.0)

#define n_n 5000000//250s
#define NR_END 1
#define FREE_ARG char *
#define NN_probe 1000 // amount of probe neurons
#define N 5                       // number of differential equations
#define NN 1000                   // number of neurons
#define conexMAX 1.0 * pow(10, 3) // each neuron max conections number
#define fe 0.8                    // % excitatory neurons (80%)
#define neuron_classe 2           // number of neurons classes
#define transient 5000           // ms
#define NMD 1000000
#define step 0.05 // ms


float ran1(long *idum);
float gasdev(long *idum);

FILE *psp;

void derivs(double y[], double df[], double *Iext, double gg_M, double *Gexc, double *Gini, double y_probe[], double df_probe[]);
double *dvector(long nl, long nh);
void free_dvector(double *v, long nl, long nh);
void nrerror(char error_text[]);
double **dmatrix(long nrl, long nrh, long ncl, long nch);
int **imatrix(long nrl, long nrh, long ncl, long nch);
void free_dmatrix(double **m, long nrl, long nrh, long ncl, long nch);
int delta(int a, int b);
void free_imatrix(int **m, long nrl, long nrh, long ncl, long nch);
int *vector(long nl, long nh);
void free_vector(int *v, long nl, long nh);


int main(void){

  int fs;
  fs = 1000; //frequency sampling Hz

  double x_probe[NN_probe +1], y_probe[NN_probe + 1], df_probe[NN_probe + 1], a_probe[NN_probe + 1], b_probe[NN_probe + 1], c_probe[NN_probe + 1];

  int i, j, t, sum, KM, numberofconnections, auxx, jj, key, qq;
  int **listaexc, *conextotalex, **listaini, *conextotalin;
  double *x, time, *a, *b, *c, *df, *y, *Iext, gg_M, I_uA, pico[NN + 2], tpeak[NN + 2], g_exc, g_ini, g;
  double IsynEXC, IsynINH, Vrev_exc, Vrev_ini, gg_total;
  long idum;
  char output_filename1[100];

  int ff;

  double *Gexc_R, *Gini_R,*Gexc_D, *Gini_D, *Gexc, *Gini;
  double tauR, tauD, delta_T, syn_norm;

  tauR = 0.5;
  tauD = 5.0;
  delta_T = ((tauD * tauR) / (tauD - tauR)) * log(tauD / tauR);
  syn_norm = 1/(-exp(-delta_T / tauR) + exp(-delta_T / tauD));
  ////////////////////////////////////////////////////////////////////////

  y = dvector(1, N * NN + 1);
  df = dvector(1, N * NN + 1);
  x = dvector(1, N * NN + 1);
  a = dvector(1, N * NN + 1);
  b = dvector(1, N * NN + 1);
  c = dvector(1, N * NN + 1);
  Iext = dvector(1, NN + 1);
  Gexc_R = dvector(1, NN + 1);
  Gini_R = dvector(1, NN + 1);
  Gexc_D = dvector(1, NN + 1);
  Gini_D = dvector(1, NN + 1);
  Gexc = dvector(1, NN + 1);
  Gini = dvector(1, NN + 1);
  conextotalex = vector(1, NN + 2);
  listaexc = imatrix(1, NN + 1, 1, conexMAX + 2);
  conextotalin = vector(1, NN + 2);
  listaini = imatrix(1, NN + 1, 1, conexMAX + 2);

  
 // **************** Parameters ***************
  gg_M =  0.03;
  Vrev_exc = 0.0;   // mV Potencial reverso exc
  Vrev_ini = -80.0; // mV Potencial reverso inh
  I_uA = 0.000175;

  // couplings
  g = 4.0;
  g_exc = 0.001424; // nS/cm^2
  g_ini = g*g_exc; // nS/cm^2
  //
 //**********************************************

  //****************** Connections *********************
  KM = 100;
  numberofconnections = NN * KM;
  for (i = 1; i <= NN; i++){
    conextotalex[i] = 0.0;
    conextotalin[i] = 0.0;
  }

  sum = 0.0;
  for (i = 1; i <= fe * NN; i++){
    conextotalex[i] = 1.0;
    listaexc[i][1] = (int)NN * ran1(&idum) + 1;
    sum = sum + 1;
  }
  for (i = fe * NN + 1; i <= NN; i++){
    conextotalin[i] = 1.0;
    listaini[i][1] = (int)NN * ran1(&idum) + 1;
  }

  while (sum < fe * numberofconnections){
    i = (int)NN * ran1(&idum) + 1;      // i post synaptic
    j = (int)NN * fe * ran1(&idum) + 1; // j pre synaptic

    auxx = 0.0;
    for (jj = 1; jj <= conextotalex[j]; jj++)
      if (listaexc[j][jj] == i)
        auxx = 1.0;

    if (auxx == 0.0)
      if (conextotalex[j] <= 2 * KM)
        if (j != i)
        {
          conextotalex[j] = conextotalex[j] + 1;
          listaexc[j][conextotalex[j]] = i;
          sum = sum + 1;
        }
  }

  for (i = 1; i <= NN; i++)
    sum = sum + conextotalin[i];

  while (sum < numberofconnections){
    i = (int)NN * ran1(&idum) + 1;                        // i post synaptic
    j = fe * NN + (int)NN * (1.0 - fe) * ran1(&idum) + 1; // j pre synaptic

    auxx = 0.0;
    for (jj = 1; jj <= conextotalin[j]; jj++)
      if (listaini[j][jj] == i)
        auxx = 1.0;

    if (auxx == 0.0)
      if (conextotalin[j] <= 2 * KM)
        if (j != i)
        {
          conextotalin[j] = conextotalin[j] + 1;
          listaini[j][conextotalin[j]] = i;
          sum = sum + 1;
        }
  }
  /////////////////////////////////////////////

    idum = -123456789;
    // initial conditions
    for (i = 1; i <= NN; i++){
      
      x[1 + (i - 1) * N] = -20.0 * ran1(&idum) - 50.0; // V
      x[2 + (i - 1) * N] = 0.1 * ran1(&idum);// m
      x[3 + (i - 1) * N] = 0.1 * ran1(&idum); //h
      x[4 + (i - 1) * N] = 0.1 * ran1(&idum);//n
      x[5 + (i - 1) * N] = 0.0; // p

      pico[i] = 0.0;

      Gexc_R[i] = 0.0;
      Gini_R[i] = 0.0;
      Gexc_D[i] = 0.0;
      Gini_D[i] = 0.0;
      Gexc[i] = 0.0;
      Gini[i] = 0.0;
      tpeak[i] = 0.0;
      Iext[i] = I_uA;
    }
    for(i=1; i<= NN_probe; i++)
      x_probe[i] = -20.0 * ran1(&idum) - 50.0;
    //////////////////////

    sprintf(output_filename1, "PSP_g%.1f_gsyn%.3f.dat", g, g_exc *1000);
    psp = fopen(output_filename1, "wt");


    time = 0.0;
    key = 0;
    qq=1;
    ff = 0;
    //////////////////////// Time loop
    for (t = 1; t <= n_n; t++){

      time = time + step;
      
      if(time >= transient)
        ff++;

      for (i = 1; i <= N * NN; i++)
        y[i] = x[i];
      
      for(i=1; i<= NN_probe; i++)
        y_probe[i] = x_probe[i];
      

      // ------------ Runge-Kutta --------------------
      derivs(y, df, Iext, gg_M, Gexc, Gini, y_probe, df_probe);
      for (i = 1; i <= N * NN; i++)
      {
        a[i] = step * df[i];
        y[i] = x[i] + a[i] / 2.0;
      }
      for (i = 1; i <= NN_probe; i++)
      {
        a_probe[i] = step * df_probe[i];
        y_probe[i] = x_probe[i] + a_probe[i] / 2.0;
      }

      derivs(y, df, Iext, gg_M, Gexc, Gini, y_probe, df_probe);
      for (i = 1; i <= N * NN; i++)
      {
        b[i] = step * df[i];
        y[i] = x[i] + b[i] / 2.0;
      }
      for (i = 1; i <= NN_probe; i++)
      {
        b_probe[i] = step * df_probe[i];
        y_probe[i] = x_probe[i] + b_probe[i] / 2.0;
      }
      derivs(y, df, Iext, gg_M, Gexc, Gini, y_probe, df_probe);
      for (i = 1; i <= N * NN; i++)
      {
        c[i] = step * df[i];
        y[i] = x[i] + c[i];
      }
      for (i = 1; i <= NN_probe; i++)
      {
        c_probe[i] = step * df_probe[i];
        y_probe[i] = x_probe[i] + c_probe[i];
      }
      derivs(y, df, Iext, gg_M, Gexc, Gini, y_probe, df_probe);
      for (i = 1; i <= N * NN; i++)
        x[i] = x[i] + (a[i] + step * df[i]) / 6.0 + (b[i] + c[i]) / 3.0;
      
      for (i = 1; i <= NN_probe; i++)
        x_probe[i] = x_probe[i] + (a_probe[i] + step * df_probe[i]) / 6.0 + (b_probe[i] + c_probe[i]) / 3.0;
      // ----------------------------------------------


      for (i = 1; i <= NN; i++){
        Gexc_R[i] = Gexc_R[i] * exp(-step / tauR); 
        Gini_R[i] = Gini_R[i] * exp(-step / tauR);
        Gexc_D[i] = Gexc_D[i] * exp(-step / tauD); 
        Gini_D[i] = Gini_D[i] * exp(-step / tauD);

        if (x[1 + (i - 1) * N] < -20.0)
          pico[i] = 0.0;

        if (x[1 + (i - 1) * N] > pico[i]) {
          pico[i] = 1000;
          tpeak[i] = time;
        }
        
        if(time == tpeak[i] + 0 * step){
          if (i <= fe * NN)
            for (j = 1; j <= conextotalex[i]; j++){
              Gexc_R[listaexc[i][j]] = Gexc_R[listaexc[i][j]] + exp(-step/tauR);
              Gexc_D[listaexc[i][j]] = Gexc_D[listaexc[i][j]] + exp(-step/tauD);
              }
          else
            for (j = 1; j <= conextotalin[i]; j++){
              Gini_R[listaini[i][j]] = Gini_R[listaini[i][j]] + exp(-step/tauR);
              Gini_D[listaini[i][j]] = Gini_D[listaini[i][j]] + exp(-step/tauD);
              }
        }

        Gexc[i] = g_exc * syn_norm * (Gexc_D[i] - Gexc_R[i]);
        Gini[i] = g_ini * syn_norm * (Gini_D[i] - Gini_R[i]);
      }


    ////////////////////////PSP /////////////////////////////////////////
    gg_total = 0.01; // g_leak mS/cm^2
    
    if(time >= transient)
      if(ff == (1000/fs)/step){ 
          ff = 0;

          IsynEXC = 0.0;
          IsynINH = 0.0;
          for(i=1; i<=NN_probe; i++){
            IsynEXC = IsynEXC + Gexc[i] * (Vrev_exc -  x_probe[i]);
            IsynINH = IsynINH + Gini[i] * (Vrev_ini -  x_probe[i]);
          }
          IsynEXC = IsynEXC / NN_probe;
          IsynINH = IsynINH / NN_probe;
          fprintf(psp, "%.3f \t %.6f \n", time/1000.0 - transient/1000.0, IsynEXC/gg_total + IsynINH/gg_total);
          qq++;
        }
    /////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////

    } 
      // End time loop


  fclose(psp);

  
  free_dvector(y, 1, N * NN + 1);
  free_dvector(df, 1, N * NN + 1);
  free_dvector(x, 1, N * NN + 1);
  free_dvector(a, 1, N * NN + 1);
  free_dvector(b, 1, N * NN + 1);
  free_dvector(c, 1, N * NN + 1);

  free_dvector(Iext, 1, N * NN + 1);

  free_dvector(Gexc_R, 1, NN + 1);
  free_dvector(Gini_R, 1, NN + 1);
  free_dvector(Gexc_D, 1, NN + 1);
  free_dvector(Gini_D, 1, NN + 1);
  free_dvector(Gexc, 1, NN + 1);
  free_dvector(Gini, 1, NN + 1);

  free_vector(conextotalex, 1, NN + 2);
  free_vector(conextotalin, 1, NN + 2);
  free_imatrix(listaexc, 1, NN + 1, 1, conexMAX + 2);
  free_imatrix(listaini, 1, NN + 1, 1, conexMAX + 2);


  return 0;
}

////////// Model
void derivs(double y[], double df[], double *Iext, double gg_M, double *Gexc, double *Gini, double y_probe[], double df_probe[]){
  int i, ii, neurontype;
  double C_m, E_Na, E_K, E_Ca;
  double V_T[neuron_classe + 1], E_leak[neuron_classe + 1], g_leak[neuron_classe + 1], g_Na[neuron_classe + 1], g_Kd[neuron_classe + 1], g_M[neuron_classe + 1], tau_max[neuron_classe + 1];
  double V, m, h, n, p, I_Na, alpha_m, beta_m, alpha_h, beta_h, dm, dh, I_Kd, alpha_n, beta_n, dn, I_M, p_inf, tau_p, dp;
  double Area[neuron_classe + 1];
  double V_x[neuron_classe + 1], g_L[neuron_classe + 1], g_T[neuron_classe + 1];
  double q, r, I_L, alpha_q, beta_q, alpha_r, beta_r, dq, dr, s_inf, I_T, u, u_inf, tau_u, du;
  double cai, dcai, drivechannel, depth, cai_inf, tau_r;
  double Vr_exc, Vr_ini;

  C_m = 1.0;    // uF/cm^2
  E_Na = 50.0;  // mV
  E_K = -100.0; //mV
  depth = 1.0;
  cai_inf = 0.00024;
  tau_r = 50.0;
  Vr_exc = 0.0;   // mV 
  Vr_ini = -80.0; // mV

  neurontype = 1;
  Area[neurontype] = 0.0096*0.0096*PI; // cm^2
  V_T[neurontype] = -55.0; // mV
  E_leak[neurontype] = -85.0; // mV
  g_leak[neurontype] = 0.01; // mS/cm^2
  g_Na[neurontype] = 50.0; // mS/cm^2
  g_Kd[neurontype] = 5.0; // mS/cm^2
  g_M[neurontype] = gg_M; // mS/cm^2
  tau_max[neurontype] = 1000.0; // ms
  V_x[neurontype] = 2.0; // mV
  g_L[neurontype] = 0.0; // mS/cm^2
  g_T[neurontype] = 0.0; // mS/cm^2

  
  for (i = 1; i <= NN; i++){
    ii = 1;

    V = y[1 + (i - 1) * N];
    m = y[2 + (i - 1) * N];
    h = y[3 + (i - 1) * N];
    n = y[4 + (i - 1) * N];
    p = y[5 + (i - 1) * N];


    // sodium current responsible for action potentials
    I_Na = g_Na[ii] * pow(m, 3) * h * (V - E_Na);
    alpha_m = (-0.32 * (V - V_T[ii] - 13.0)) / (exp(-(V - V_T[ii] - 13.0) / 4.0) - 1.0);
    beta_m = (0.28 * (V - V_T[ii] - 40.0)) / (exp((V - V_T[ii] - 40.0) / 5.0) - 1.0);
    alpha_h = 0.128 * exp(-(V - V_T[ii] - 17.0) / 18.0);
    beta_h = 4.0 / (1.0 + exp(-(V - V_T[ii] - 40.0) / 5.0));

    dm = alpha_m * (1.0 - m) - beta_m * m;
    dh = alpha_h * (1.0 - h) - beta_h * h;

    // potassium current responsible for action potentials
    I_Kd = g_Kd[ii] * (pow(n, 4) * (V - E_K));
    alpha_n = (-0.032 * (V - V_T[ii] - 15.0)) / (exp(-(V - V_T[ii] - 15.0) / 5.0) - 1.0);
    beta_n = 0.5 * exp(-(V - V_T[ii] - 10.0) / 40.0);

    dn = alpha_n * (1.0 - n) - beta_n * n;

    // slow voltage-dependent potassium current responsible for spike-frequency adaptation
    I_M = g_M[ii] * p * (V - E_K);
    p_inf = 1.0 / (1.0 + exp(-(V + 35.0) / 10.0));
    tau_p = tau_max[ii] / (3.3 * exp((V + 35.0) / 20.0) + exp(-(V + 35.0) / 20.0));

    dp = (p_inf - p) / tau_p;


    df[1 + (i - 1) * N] = (1.0 / C_m) * (-g_leak[ii] * (V - E_leak[ii]) - I_Na - I_Kd - I_M + (Iext[i] / Area[ii]) + Gexc[i] * (Vr_exc - V) + Gini[i] * (Vr_ini - V));
    df[2 + (i - 1) * N] = dm;
    df[3 + (i - 1) * N] = dh;
    df[4 + (i - 1) * N] = dn;
    df[5 + (i - 1) * N] = dp;

  }
  //////// Probe neuron /////////
  for(i = 1; i <= NN_probe; i++){
    V = y_probe[i];
    df_probe[i] = (1.0 / C_m) * (-g_leak[ii] * (V - E_leak[ii]) + Gexc[i] * (Vr_exc - V) + Gini[i] * (Vr_ini - V));
  }
}
/////////////////////////////////////////



double *dvector(long nl, long nh)
{
  double *v;

  v = (double *)malloc((size_t)((nh - nl + 1 + NR_END) * sizeof(double)));
  if (!v)
    nrerror("allocation failure in dvector()");
  return v - nl + NR_END;
}

void free_dvector(double *v, long nl, long nh)
{
  free((FREE_ARG)(v + nl - NR_END));
}

void nrerror(char error_text[])
{
  fprintf(stderr, "Numerical Recipes run-time error...\n");
  fprintf(stderr, "%s\n", error_text);
  fprintf(stderr, "...now exiting to system...\n");
  exit(1);
}

float ran1(long *idum)
{
  int j;
  long k;
  static long iy = 0;
  static long iv[NTAB];
  float temp;

  if (*idum <= 0 || !iy)
  {
    if (-(*idum) < 1)
      *idum = 1;
    else
      *idum = -(*idum);
    for (j = NTAB + 7; j >= 0; j--)
    {
      k = (*idum) / IQ;
      *idum = IA * (*idum - k * IQ) - IR * k;
      if (*idum < 0)
        *idum += IM;
      if (j < NTAB)
        iv[j] = *idum;
    }
    iy = iv[0];
  }
  k = (*idum) / IQ;
  *idum = IA * (*idum - k * IQ) - IR * k;
  if (*idum < 0)
    *idum += IM;
  j = iy / NDIV;
  iy = iv[j];
  iv[j] = *idum;
  if ((temp = AM * iy) > RNMX)
    return RNMX;
  else
    return temp;
}

float gasdev(long *idum)
{
  float ran1(long *idum);
  static int iset = 0;
  static float gset;
  float fac, rsq, v1, v2;

  if (*idum < 0)
    iset = 0;
  if (iset == 0)
  {
    do
    {
      v1 = 2.0 * ran1(idum) - 1.0;
      v2 = 2.0 * ran1(idum) - 1.0;
      rsq = v1 * v1 + v2 * v2;
    } while (rsq >= 1.0 || rsq == 0.0);
    fac = sqrt(-2.0 * log(rsq) / rsq);
    gset = v1 * fac;
    iset = 1;
    return v2 * fac;
  }
  else
  {
    iset = 0;
    return gset;
  }
}

double **dmatrix(long nrl, long nrh, long ncl, long nch)
{
  long i, nrow = nrh - nrl + 1, ncol = nch - ncl + 1;
  double **m;

  m = (double **)malloc((size_t)((nrow + NR_END) * sizeof(double *)));
  if (!m)
    nrerror("allocation failure 1 in matrix()");
  m += NR_END;
  m -= nrl;

  m[nrl] = (double *)malloc((size_t)((nrow * ncol + NR_END) * sizeof(double)));
  if (!m[nrl])
    nrerror("allocation failure 2 in matrix()");
  m[nrl] += NR_END;
  m[nrl] -= ncl;

  for (i = nrl + 1; i <= nrh; i++)
    m[i] = m[i - 1] + ncol;

  return m;
}

void free_dmatrix(double **m, long nrl, long nrh, long ncl, long nch)
{
  free((FREE_ARG)(m[nrl] + ncl - NR_END));
  free((FREE_ARG)(m + nrl - NR_END));
}

int **imatrix(long nrl, long nrh, long ncl, long nch)
{
  long i, nrow = nrh - nrl + 1, ncol = nch - ncl + 1;
  int **m;

  m = (int **)malloc((size_t)((nrow + NR_END) * sizeof(int *)));
  if (!m)
    nrerror("allocation failure 1 in matrix()");
  m += NR_END;
  m -= nrl;

  m[nrl] = (int *)malloc((size_t)((nrow * ncol + NR_END) * sizeof(int)));
  if (!m[nrl])
    nrerror("allocation failure 2 in matrix()");
  m[nrl] += NR_END;
  m[nrl] -= ncl;

  for (i = nrl + 1; i <= nrh; i++)
    m[i] = m[i - 1] + ncol;

  return m;
}

void free_imatrix(int **m, long nrl, long nrh, long ncl, long nch)
{
  free((FREE_ARG)(m[nrl] + ncl - NR_END));
  free((FREE_ARG)(m + nrl - NR_END));
}

int *vector(long nl, long nh)
{
  int *v;

  v = (int *)malloc((size_t)((nh - nl + 1 + NR_END) * sizeof(int)));
  if (!v)
    nrerror("allocation failure in dvector()");
  return v - nl + NR_END;
}

void free_vector(int *v, long nl, long nh)
{
  free((FREE_ARG)(v + nl - NR_END));
}

