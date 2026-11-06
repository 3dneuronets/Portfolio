//~ Neuron model basead in:
//~ Biol Cybern (2008) 99:427–441
//~ DOI 10.1007/s00422-008-0263-8
//~ Minimal Hodgkin–Huxley type models for different classes
//~ of cortical and thalamic neurons
//~ Martin Pospischil · Maria Toledo-Rodriguez ·
//~ Cyril Monier · Zuzanna Piwkowska · Thierry Bal ·
//~ Yves Frégnac · Henry Markram · Alain Destexhe

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

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

#define n_n  5000000// 50s // Number of steps    total time = n_n*step
#define NR_END 1
#define FREE_ARG char *
#define N 5                       // number of equations
#define NN 1000                   // Number of neurons
#define conexMAX 1.0 * pow(10, 3) // each neuron max conections number
#define fe 0.8                    // % excitatory neurons (80%)
#define neuron_classe 2           // number of neurons classes
#define transient 100           // in ms
#define NMD 1000000 //max number of firing of a single neurons

float ran1(long *idum);
float gasdev(long *idum);

FILE *T;
FILE *Rt;
FILE *coefficient_variation;
FILE *raster; // if you run the code for a long time, 
              // the raster file will be very large, so you can comment this line and the other line that this file is used

void derivs(double y[], double df[], double *Iext, double gg_M, double *Gexc, double *Gini);
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

  int i, j, t, auxISI, sum, KM, numberofconnections, auxx, jj;
  int **listexc, *conextotalex, **listini, *conextotalin;
  double *x, time, step, *a, *b, *c, *df, *y, *Iext, gg_M, pico[NN + 2], sumISI, sumISI2, tpeak[NN + 2], *Gexc, *Gini, delay, g_exc, g_ini, g;
  double stdesv, CV, CV_mean,reobase, iCVsumISI, iCVsumISI2, iCVauxISI, iCV, contBurst;
  double CVmean, contCV, icontUP, icontDOWN, contUP, contUP2, contDOWN, timeUP, timeDOWN, ISI, ISI2, contISI;;
  double kinitial,kfinal,R,real,compl,Rmean,**nk,*phi;
  int cont,contR,*k,*kmax; 
  double  mean_time;
  long idum;
  char output_filename1[100], output_filename2[200];

  y = dvector(1, N * NN + 1);
  df = dvector(1, N * NN + 1);
  x = dvector(1, N * NN + 1);
  a = dvector(1, N * NN + 1);
  b = dvector(1, N * NN + 1);
  c = dvector(1, N * NN + 1);

  Iext = dvector(1, NN + 1);

  k=vector(1,NN+1);
  kmax=vector(1,NN+1);
  phi=dvector(1,NN+1);
  nk=dmatrix(1,NMD+2,1,NN+2);

  Gexc = dvector(1, NN + 1);
  Gini = dvector(1, NN + 1);

  conextotalex = vector(1, NN + 2);
  listexc = imatrix(1, NN + 1, 1, conexMAX + 2);

  conextotalin = vector(1, NN + 2);
  listini = imatrix(1, NN + 1, 1, conexMAX + 2);

  step = 0.05; // integration step


  //*****************************************************************
  KM = 100;
  numberofconnections = NN * KM; 

  //****************** Creating a matrix with the connections *********************
  for (i = 1; i <= NN; i++){
    conextotalex[i] = 0.0;
    conextotalin[i] = 0.0;
  }

  sum = 0.0;
  for (i = 1; i <= fe * NN; i++){
    conextotalex[i] = 1.0;
    listexc[i][1] = (int)NN * ran1(&idum) + 1;
    sum = sum + 1;
  }
  for (i = fe * NN + 1; i <= NN; i++){
    conextotalin[i] = 1.0;
    listini[i][1] = (int)NN * ran1(&idum) + 1;
  }

  //------- Exc connection list---------//
  while (sum < fe * numberofconnections){
    i = (int)NN * ran1(&idum) + 1;      // post synaptic
    j = (int)NN * fe * ran1(&idum) + 1; // pre synaptic

    auxx = 0.0;
    for (jj = 1; jj <= conextotalex[j]; jj++)
      if (listexc[j][jj] == i)
        auxx = 1.0;

    if (auxx == 0.0)
      if (conextotalex[j] <= 2 * KM)
        if (j != i)
        {
          conextotalex[j] = conextotalex[j] + 1;
          listexc[j][conextotalex[j]] = i;
          sum = sum + 1;
        }
  }
  //------- Inh connection list---------//
  for (i = 1; i <= NN; i++)
    sum = sum + conextotalin[i];

  while (sum < numberofconnections){
    i = (int)NN * ran1(&idum) + 1;                        // post synaptic
    j = fe * NN + (int)NN * (1.0 - fe) * ran1(&idum) + 1; // pre synaptic

    auxx = 0.0;
    for (jj = 1; jj <= conextotalin[j]; jj++)
      if (listini[j][jj] == i)
        auxx = 1.0;

    if (auxx == 0.0)
      if (conextotalin[j] <= 2 * KM)
        if (j != i)
        {
          conextotalin[j] = conextotalin[j] + 1;
          listini[j][conextotalin[j]] = i;
          sum = sum + 1;
        }
  }
  /////////////////////////////////////////////

  //*****************************************************************
  


  ///////////// Initial conditions ///////////////
  for (i = 1; i <= NN; i++){
    idum = -123456789;
    x[1 + (i - 1) * N] = -20.0 * ran1(&idum) - 50.0;
    x[2 + (i - 1) * N] = 0.1 * ran1(&idum);
    x[3 + (i - 1) * N] = 0.1 * ran1(&idum);
    x[4 + (i - 1) * N] = 0.1 * ran1(&idum);
    x[5 + (i - 1) * N] = 0.0;
    pico[i] = 0.0;
    Gexc[i] = 0.0;
    Gini[i] = 0.0;
    tpeak[i] = 0.0;
    Iext[i] = 0.000175; // external current (I_ext)

    k[i]=0.0;               // Counter for the number of spikes of a neuron
    kmax[i]=0.0;	         // Counter for the total number of spikes of a neuron
    nk[1][i]=0.0;           // time when the spikes of a neuron occur
  }
  ///////////////////////////////////////////////

  gg_M =  0.03; // Slow potassium conductance
  g_exc = 0.001835; // nS/cm^2 // coupling strength (g_syn)
  g = 4.0; // g_ini/g_exc = g
  g_ini = g * g_exc; // nS/cm^2

  auxISI = 0;
  sumISI = 0;
  sumISI2 = 0;
  time = 0.0;
  contBurst = 0.0;
  iCVsumISI = 0;
  iCVsumISI2 = 0;
  iCVauxISI = 0;
  time = 0.0; 
  t = 0;

  sprintf(output_filename2, "T_gsyn%.6f.dat", g_exc);
  T = fopen(output_filename2, "wt");

  sprintf(output_filename2, "CVt_gsyn%.6f.dat", g_exc);
  coefficient_variation = fopen(output_filename2, "wt");

  sprintf(output_filename2, "Rt_gsyn%.6f.dat", g_exc);
  Rt = fopen(output_filename2, "wt");

  sprintf(output_filename2, "Raster_gsyn%.6f.dat", g_exc);
  raster = fopen(output_filename2, "wt");

  ////////// Time loop ////////////////////////////
  int tt;
  tt = 0;
  while(tt<n_n){
    tt = tt + 1;
    time = time + step;

    for (i = 1; i <= N * NN; i++)
      y[i] = x[i];

    // ------------ 4th order Runge-Kutta --------------------
    derivs(y, df, Iext, gg_M, Gexc, Gini);
    for (i = 1; i <= N * NN; i++)
    {
      a[i] = step * df[i];
      y[i] = x[i] + a[i] / 2.0;
    }
    derivs(y, df, Iext, gg_M, Gexc, Gini);
    for (i = 1; i <= N * NN; i++)
    {
      b[i] = step * df[i];
      y[i] = x[i] + b[i] / 2.0;
    }
    derivs(y, df, Iext, gg_M, Gexc, Gini);
    for (i = 1; i <= N * NN; i++)
    {
      c[i] = step * df[i];
      y[i] = x[i] + c[i];
    }
    derivs(y, df, Iext, gg_M, Gexc, Gini);
    for (i = 1; i <= N * NN; i++)
      x[i] = x[i] + (a[i] + step * df[i]) / 6.0 + (b[i] + c[i]) / 3.0;
    // ----------------------------------------------

    mean_time = 0.0;

    //// Computing the spikes /////
    for (i = 1; i <= NN; i++){
      mean_time = mean_time + (time - tpeak[i]); // <T>

      Gexc[i] = Gexc[i] * exp(-step / 5.0); 
      Gini[i] = Gini[i] * exp(-step / 5.0);

      //  triggers when the potential V_i exceeds 0 mV
      if (x[1 + (i - 1) * N] < -20.0)
        pico[i] = 0.0;

      if (x[1 + (i - 1) * N] > pico[i]) {

        if(i <= 200)
          fprintf(raster, "%.3f \t %i \n", time, i);

        pico[i] = 1000;

        if (time > transient && tpeak[i] > 0.0){
          sumISI = sumISI + (time - tpeak[i]);
          sumISI2 = sumISI2 + (time - tpeak[i]) * (time - tpeak[i]);

          auxISI = auxISI + 1;
        }

        if(time>transient && k[i]<NMD){ //Saving the spikes and the time they occur for each neuron
              
              k[i]=k[i]+1;     
              nk[k[i]][i]=time;
				   
              if(k[i]==1.0) 
                kinitial=time;				   		       
				}	

        tpeak[i] = time;

        if (i <= fe * NN)
          for (j = 1; j <= conextotalex[i]; j++)
            Gexc[listexc[i][j]] = Gexc[listexc[i][j]] + g_exc;
        else
          for (j = 1; j <= conextotalin[i]; j++)
            Gini[listini[i][j]] = Gini[listini[i][j]] + g_ini;
      }
    }

    mean_time = mean_time / NN;
    fprintf(T, "%.3f \t %.6f \n", time, mean_time);
  } 
  ////////// End of time loop //////////////////////

//////////////////// Calculating the Kuramoto order parameter R(t)//////////////////////
  time=0.0;
  Rmean=0.0;
  contR=0.0;
  kfinal=n_n*step;

  for(i=1;i<=NN;i=i+1){
    phi[i]=0.0;
    kmax[i]=k[i];
    k[i]=1.0;	

    if(kmax[i]>1)    
      if(kfinal>nk[kmax[i]][i] && kfinal>kinitial)
        kfinal=nk[kmax[i]][i];
  }

  for(time=transient;time<=n_n*step;time=time+2.0*step)
  {
    for(i=1;i<=NN;i=i+1)
      if(kmax[i]>1)
        if(time>nk[k[i]][i] && time<nk[kmax[i]][i])
        {
        if(time<=nk[k[i]+1][i])	  
          phi[i]=2*PI*(time-nk[k[i]][i])/(nk[k[i]+1][i]-nk[k[i]][i]); //+2*PI*k[i]
              
        if(time>=nk[k[i]+1][i])
          k[i]=k[i]+1;		         
        }

    
    if(time>=kinitial && time<=kfinal){
      real=0.0;
      compl=0.0;
      cont=0;
      for(i=1;i<=NN;i++)
        if(kmax[i]>1)
          {
          real=real+cos(phi[i]);
          compl=compl+sin(phi[i]); 
          cont=cont+1;
          }
      
      real=real/cont;
      compl=compl/cont;
      
      R=sqrt(real*real+compl*compl);
      Rmean=Rmean+R;
      contR=contR+1.0;
      fprintf(Rt, "%.4f \t %.6f \n", time, R);
      
    }
  }
  //////////////// End of calculating R(t) //////////////////////////

  //////////////// Calculating CV(t) //////////////////////////
  time=0.0;
  CVmean=0.0;
  contCV=0.0;
  icontUP=0.0;
  icontDOWN=0.0;
  contUP=0.0;
  contUP2=0.0;
  contDOWN=0.0;
  timeUP=0.0;
  timeDOWN=0.0;

  for(i=1;i<=NN;i=i+1){
    phi[i]=0.0;
    kmax[i]=k[i];
    k[i]=1.0;	
  }
          
  for(time=transient;time<=n_n*step;time=time+10.0 * step){  
    ISI=0;		  	
    ISI2=0;	
    contISI=0; 	
    
    for(i=1;i<=0.1*NN;i=i+1)
      if(time>nk[k[i]][i] && time<nk[kmax[i]][i]){	
          if(k[i]>5 && k[i]<kmax[i]-5)
        for(j=4;j>=-5;j=j-1) {
          ISI=ISI+(nk[k[i]+1+j][i]-nk[k[i]+j][i]);		  	
          ISI2=ISI2+(nk[k[i]+1+j][i]-nk[k[i]+j][i])*(nk[k[i]+1+j][i]-nk[k[i]+j][i]);
          contISI=contISI+1;
          } 

      if(time>=nk[k[i]+1][i])
      k[i]=k[i]+1;		         
      }	  
      
        if(contISI>0){	
          stdesv=sqrt(ISI2/contISI - (ISI/contISI)*(ISI/contISI));
          CV = stdesv/(ISI/contISI); //CV		
          CVmean=CVmean+CV;
          contCV=contCV+1.0;
          fprintf(coefficient_variation, "%.4f \t %.6f \n", time, CV);
      }	  
  }
  //////////////// End of calculating CV(t) //////////////////////////
    
  fclose(Rt);
  fclose(coefficient_variation);
  fclose(T);
  fclose(raster);
  
  free_dvector(y, 1, N * NN + 1);
  free_dvector(df, 1, N * NN + 1);
  free_dvector(x, 1, N * NN + 1);
  free_dvector(a, 1, N * NN + 1);
  free_dvector(b, 1, N * NN + 1);
  free_dvector(c, 1, N * NN + 1);

  free_dvector(Iext, 1, N * NN + 1);

  free_vector(k,1,NN+1); 
  free_vector(kmax,1,NN+1);
  free_dvector(phi,1,NN+1); 
  free_dmatrix(nk,1,NMD+2,1,NN+2);

  free_dvector(Gexc, 1, NN + 1);
  free_dvector(Gini, 1, NN + 1);

  free_vector(conextotalex, 1, NN + 2);
  free_vector(conextotalin, 1, NN + 2);
  free_imatrix(listexc, 1, NN + 1, 1, conexMAX + 2);
  free_imatrix(listini, 1, NN + 1, 1, conexMAX + 2);


  return 0;
}

////////// Equations of the model //////////
void derivs(double y[], double df[], double *Iext, double gg_M, double *Gexc, double *Gini){
  int i, ii, neurontype;
  double C_m, E_Na, E_K;
  double V_T[neuron_classe + 1], E_leak[neuron_classe + 1], g_leak[neuron_classe + 1], g_Na[neuron_classe + 1], g_Kd[neuron_classe + 1], g_M[neuron_classe + 1], tau_max[neuron_classe + 1];
  double V, m, h, n, p, I_Na, alpha_m, beta_m, alpha_h, beta_h, dm, dh, I_Kd, alpha_n, beta_n, dn, I_M, p_inf, tau_p, dp;
  double Area[neuron_classe + 1];
  double depth;
  double Vr_exc, Vr_ini;

  C_m = 1.0;    // uF/cm^2
  E_Na = 50.0;  // mV
  E_K = -100.0; //mV
  depth = 1.0;
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

  ////////////////////////// Coupled equations////////////////////
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