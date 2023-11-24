// In this file, we use xgboost to predict the states of each appliance
// and record runtime of preprocessing and model's inference, which are main cost of inference.

#include <stdio.h>
#include <stdlib.h>
#include <fftw3.h>
#include <math.h>
#include <time.h>
#include <xgboost/c_api.h>

#define FILECYCLE 70172 // Before run the program, you need check the number of cycle in the data.bin file( from ConvertFormat.py' output, here we check dataset 0)

int data[FILECYCLE][320];
float modelInput[30];

float predResult[FILECYCLE];
float littleResult[10][FILECYCLE];

void convertFormat(fftw_complex *fftIn)
{
  for (int i = 0; i < 10; i++)
  {
    modelInput[i + 10] = fftIn[i][1] / 161;
    modelInput[i + 20] = fftIn[i][0] / 161;
    modelInput[i] = sqrt(modelInput[i + 10] * modelInput[i + 10] + modelInput[i + 20] * modelInput[i + 20]);
  }
  modelInput[0] = modelInput[0] + modelInput[1];
  modelInput[10] = modelInput[10] + modelInput[11];
  modelInput[20] = modelInput[20] + modelInput[21];
}

void convertFormat2(fftw_complex *fftIn, int width)
{
  for (int i = 0; i < 10; i++)
  {
    modelInput[i + 10] = fftIn[i][1] / width;
    modelInput[i + 20] = fftIn[i][0] / width;
    modelInput[i] = sqrt(modelInput[i + 10] * modelInput[i + 10] + modelInput[i + 20] * modelInput[i + 20]);
  }
  modelInput[0] = modelInput[0] + modelInput[1];
  modelInput[10] = modelInput[10] + modelInput[11];
  modelInput[20] = modelInput[20] + modelInput[21];
}

int main(int argc, char **argv)
{
  if(argc < 2){
    printf("Error, Usage %s [file that contain model files]")
  }
  FILE *file = fopen("data.bin", "rb");
  if (file == NULL)
  {
    perror("Unable to open the file");
    return 1;
  }

  int rows = FILECYCLE; // row of read data
  int cols = 320;       // col of read data
  clock_t start, end;
  double cpu_time_used;

  BoosterHandle booster;

  // do something with booster
  const char *fname[128];
  sprintf(fname, "%s/all.model", argv[1]);
  printf("%s\n", fname);
  (XGBoosterCreate(NULL, 0, &booster));
  int retCode = (XGBoosterLoadModel(booster, fname));
  if (retCode != 0)
  {
    printf("load model failed, error code: %d\n", retCode);
    return -1;
  }

  DMatrixHandle dmatrix;
  bst_ulong out_len;
  const float *out_result;

  fread(data, sizeof(int), rows * cols, file);

  fclose(file);

  int largeLen = 320; // Length of input for large power appliance
  fftw_complex *fftIn, *fftOut;
  fftw_plan largeP;
  fftOut = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * largeLen);
  fftIn = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * largeLen);

  // Create large power appliance plan
  largeP = fftw_plan_dft_1d(largeLen, fftIn, fftOut, FFTW_FORWARD, FFTW_ESTIMATE);
  start = clock();

  // Here we const the segment position of Segmented differential current for each kind of little power appliance
  int llPos[5] = {69, 64, 51, 51, 48};
  int lrPos[5] = {88, 88, 88, 88, 86};
  int rlPos[5] = {230, 222, 213, 213, 208};
  int rrPos[5] = {248, 248, 248, 248, 246};

  BoosterHandle littleBooster[10];
  const char *litFileName[10][128];

  for (int i = 0; i < 10; i++)
  {
    sprintf(litFileName[i], "%s/little-%d.model", argv[1], i);
  }

  for (int i = 0; i < 10; i++)
  {
    (XGBoosterCreate(NULL, 0, &littleBooster[i]));
    int retCode = (XGBoosterLoadModel(littleBooster[i], litFileName[i]));
    if (retCode != 0)
    {
      printf("load model failed, error code: %d\n", retCode);
      return -1;
    }
  }

  fftw_plan littleP[5];
  int lFFTLen[5];
  for (int i = 0; i < 5; i++)
  {
    lFFTLen[i] = lrPos[i] - llPos[i] + rrPos[i] - rlPos[i];
    littleP[i] = fftw_plan_dft_1d(lFFTLen[i], fftIn, fftOut, FFTW_FORWARD, FFTW_ESTIMATE);
  }

  for (int i = 0; i < FILECYCLE; i++)
  {
    for (int j = 0; j < 320; j++)
    {
      fftIn[j][0] = data[i][j];
      fftIn[j][1] = 0;
    }
    fftw_execute(largeP);

    convertFormat(fftOut);

    XGDMatrixCreateFromMat((float *)modelInput, 1, 30, -1, &dmatrix);
    XGBoosterPredict(booster, dmatrix, 0, 0, 0, &out_len, &out_result);
    predResult[i] = out_result[0];

    for (int k = 0; k < 5; k++)
    {
      for (int j = llPos[k]; j < lrPos[k]; j++)
      {
        fftIn[j - llPos[k]][0] = data[i][j];
        fftIn[j - llPos[k]][1] = 0;
      }
      for (int j = rlPos[k]; j < rrPos[k]; j++)
      {
        fftIn[j - rlPos[k] + lrPos[k] - llPos[k]][0] = data[i][j];
        fftIn[j - rlPos[k] + lrPos[k] - llPos[k]][1] = 0;
      }
      fftw_execute(littleP[k]);
      convertFormat2(fftOut, lFFTLen[k]);
      XGDMatrixCreateFromMat((float *)modelInput, 1, 30, -1, &dmatrix);
      XGBoosterPredict(littleBooster[2 * k], dmatrix, 0, 0, 0, &out_len, &out_result);
      littleResult[2 * k][i] = out_result[0];
      XGBoosterPredict(littleBooster[2 * k + 1], dmatrix, 0, 0, 0, &out_len, &out_result);
      littleResult[2 * k + 1][i] = out_result[0];
    }
  }
  end = clock();

  cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
  printf("cpu_time_used = %f \n", cpu_time_used);
  fftw_destroy_plan(largeP);

  fftw_free(fftIn);
  fftw_free(fftOut);

  XGBoosterFree(booster);
  XGDMatrixFree(dmatrix);
  return 0;
}