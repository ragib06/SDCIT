//
// Created by Sanghack Lee on 3/14/17.
//

#ifndef C_KCIPT_SDCIT_H
#define C_KCIPT_SDCIT_H

#include <algorithm>
#include <random>

void c_sdcit(const double *K_XZ, const double *K_Y, const double *D_Z_, const int n,
             const int b, const int seed, const int n_threads,
             double *const mmsd, double *const null);

std::pair<std::vector<int>, std::vector<std::pair<int, int> >> perm_and_mask(const std::vector<double> &D_Z, const int n, const std::vector<int> &sample, std::mt19937 &generator);

std::vector<double> shuffle_matrix(const double *mat, const int n, const std::vector<int> &perm);

std::vector<double> penalized_distance(const std::vector<double> &D_Z, const int n, const std::vector<std::pair<int, int> > mask);
#endif //C_KCIPT_SDCIT_H
