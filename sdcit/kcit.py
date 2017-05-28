import os
import warnings

import numpy as np
import scipy
import scipy.linalg
from numpy import eye, exp, sqrt, trace, diag, zeros
from scipy.stats import chi2, gamma
from sklearn.metrics import pairwise_distances

from sdcit.utils import centering


def np2matlab(arr):
    import matlab.engine

    return matlab.double([[float(v) for v in row] for row in arr])


def kcit(x, y, z, seed=None, mateng=None, installed_at='~/Dropbox/research/2014 rcm/workspace/python/SDCIT/kcit'):
    """Python-wrapper for KCIT by Zhang et al. (2011)"""
    import matlab.engine

    not_given = mateng is None
    try:
        if not_given:
            mateng = matlab.engine.start_matlab()
            dir_at = os.path.expanduser(installed_at)
            mateng.addpath(mateng.genpath(dir_at))

        if seed is not None:
            mateng.RandStream.setGlobalStream(mateng.RandStream('mcg16807', 'Seed', seed))
        statistic, v2, boot_p_value, v3, appr_p_value = mateng.CInd_test_new_withGP(np2matlab(x), np2matlab(y), np2matlab(z), 0.01, 0, nargout=5)
        return statistic, v2, boot_p_value, v3, appr_p_value
    finally:
        if not_given and mateng is not None:
            mateng.quit()


def kcit_lee(Kx, Ky, Kz, seed=None, mateng=None, installed_at='~/Dropbox/research/2014 rcm/workspace/python/SDCIT/kcit'):
    warnings.warn('KCIT without hyperparameter optimization')
    import matlab.engine

    not_given = mateng is None
    try:
        if not_given:
            mateng = matlab.engine.start_matlab()
            dir_at = os.path.expanduser(installed_at)
            mateng.addpath(mateng.genpath(dir_at))

        if seed is not None:
            mateng.RandStream.setGlobalStream(mateng.RandStream('mcg16807', 'Seed', seed))
        _, _, _, _, appr_p_value = mateng.CInd_test_new_withGP_Lee(Kx, Ky, Kz, 0.01, nargout=5)
        return appr_p_value
    finally:
        if not_given and mateng is not None:
            mateng.quit()


def reduce_eig(eig_Ky, eiy=None, Thresh=1e-5):
    IIy = np.where(eig_Ky > max(eig_Ky) * Thresh)[0]
    if eiy is not None:
        return eig_Ky[IIy], eiy[:, IIy]
    else:
        return eig_Ky[IIy]


def normalizes(xs):
    return [normalize(x) for x in xs]


def normalize(x: np.ndarray) -> np.ndarray:
    """normalize per column"""
    x = x - np.vstack([np.mean(x, 0)] * len(x))
    x = x / np.std(x, 0)  # broadcast
    return x


def gamcdf(t, a, b):
    return gamma.cdf(t, a, scale=b)


def gaminv(q, a, b):
    return gamma.ppf(q, a, scale=b)


def chi2rnd(df, m, n):
    return chi2.rvs(df, size=m * n).reshape((m, n))


def eigdec(x: np.ndarray, N: int):
    M = len(x)
    # ascending M-1-N <= <= M-1
    w, v = scipy.linalg.eigh(x, eigvals=(M - 1 - N + 1, M - 1))
    w = w[::-1]
    v = v[:, ::-1]
    return w, v


# inverse of a positive definite matrix
def pdinv(x):
    L = scipy.linalg.cholesky(x)
    Linv = scipy.linalg.inv(L)
    return Linv.T @ Linv


def kernel(x, xKern=None, theta=0):
    if xKern is None:
        xKern = x
    n2 = pairwise_distances(x, xKern, metric='sqeuclidean')
    if theta == 0:
        theta = 2 / np.median(n2[np.tril(n2) > 0])

    wi2 = theta / 2
    kx = exp(-n2 * wi2)
    return kx


def python_kcit(x: np.ndarray, y: np.ndarray, z: np.ndarray, alpha=0.05, width=0.0, with_gp=False, noise=1e-3, num_bootstrap_for_null=5000):
    Num_eig = T = len(y)

    x, y, z = normalize(x), normalize(y), normalize(z)
    D = z.shape[1]

    width = width_heuristic_by_zhang(T, width)

    theta = 1 / (width ** 2 * D)
    Kx = centering(kernel(np.hstack([x, z / 2]), theta=theta))
    Ky = centering(kernel(y, theta=theta))

    I = eye(T)
    if with_gp:
        import GPflow
        eig_Kx, eix = reduce_eig(*eigdec((Kx + Kx.T) / 2, min(400, int(T / 4))))
        eig_Ky, eiy = reduce_eig(*eigdec((Ky + Ky.T) / 2, min(200, int(T / 5))))

        gp_x = GPflow.gpr.GPR(z, 2 * sqrt(T) * eix @ diag(sqrt(eig_Kx)) / sqrt(eig_Kx[0]), GPflow.kernels.RBF(D) + GPflow.kernels.White(D))
        gp_y = GPflow.gpr.GPR(z, 2 * sqrt(T) * eiy @ diag(sqrt(eig_Ky)) / sqrt(eig_Ky[0]), GPflow.kernels.RBF(D) + GPflow.kernels.White(D))
        gp_x.optimize()
        gp_y.optimize()

        Kz_x = gp_x.kern.rbf.compute_K_symm(z)
        Kz_y = gp_y.kern.rbf.compute_K_symm(z)

        P1_x = I - Kz_x @ pdinv(Kz_x + gp_x.kern.white.variance.value[0] * I)
        P1_y = I - Kz_y @ pdinv(Kz_y + gp_y.kern.white.variance.value[0] * I)
    else:
        Kz = centering(kernel(z, theta=theta))
        P1_x = P1_y = (I - Kz @ pdinv(Kz + noise * I))

    Kxz = P1_x @ Kx @ P1_x.T
    Kyz = P1_y @ Ky @ P1_y.T
    test_statistic = trace(Kxz @ Kyz)

    eig_Kxz, eivx = reduce_eig(*eigdec((Kxz + Kxz.T) / 2, Num_eig))
    eig_Kyz, eivy = reduce_eig(*eigdec((Kyz + Kyz.T) / 2, Num_eig))

    eiv_prodx = eivx @ diag(sqrt(eig_Kxz))
    eiv_prody = eivy @ diag(sqrt(eig_Kyz))

    num_eigx = eiv_prodx.shape[1]  # size(eiv_prodx, 2)
    num_eigy = eiv_prody.shape[1]  # size(eiv_prody, 2)
    size_u = num_eigx * num_eigy
    uu = zeros((T, size_u))
    for i in range(num_eigx):
        for j in range(num_eigy):
            uu[:, i * num_eigy + j] = eiv_prodx[:, i] * eiv_prody[:, j]

    uu_prod = uu @ uu.T if size_u > T else uu.T @ uu
    eig_uu = reduce_eig(eigdec(uu_prod, min(T, size_u))[0])

    critical_val, p_val = null_by_bootstrap(test_statistic, num_bootstrap_for_null, alpha, eig_uu[:, None])
    approx_critical_val, approx_p_val = null_by_gamma_approx(test_statistic, alpha, uu_prod)

    return test_statistic, critical_val, p_val, approx_critical_val, approx_p_val


def width_heuristic_by_zhang(T, width):
    if width == 0:
        if T <= 200:
            width = 1.2
        elif T < 1200:
            width = 0.7
        else:
            width = 0.4
    return width


def null_by_gamma_approx(Sta, alpha, uu_prod):
    """critical value and p-value based on Gamma distribution approximation"""
    mean_appr = trace(uu_prod)
    var_appr = 2 * trace(uu_prod ** 2)
    k_appr = mean_appr ** 2 / var_appr
    theta_appr = var_appr / mean_appr
    Cri_appr = gaminv(1 - alpha, k_appr, theta_appr)
    p_appr = 1 - gamcdf(Sta, k_appr, theta_appr)
    return Cri_appr, p_appr


def null_by_bootstrap(Sta, T_BS, alpha, eig_uu):
    """critical value and p-value based on bootstrapping"""
    null_dstr = eig_uu.T @ chi2rnd(1, len(eig_uu), T_BS)
    null_dstr = np.sort(null_dstr.squeeze())

    critical_val = null_dstr[int((1 - alpha) * T_BS)]
    p_val = np.sum(null_dstr > Sta) / T_BS
    return critical_val, p_val
