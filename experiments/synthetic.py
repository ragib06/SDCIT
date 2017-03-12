import numpy as np
from numpy import zeros, tanh
from numpy.random import rand, randn


def henon(seed, n, gamma, independence, noise_dim=2, noise_std=0.5):
    np.random.seed(seed)

    # 2N x (2 + noise_dim)
    # first half is used to warm up chaotic series...
    x = np.hstack([zeros((2 * n, 2)), noise_std * randn(2 * n, noise_dim)])
    y = np.hstack([zeros((2 * n, 2)), noise_std * randn(2 * n, noise_dim)])

    assert x.shape == (2 * n, 2 + noise_dim)

    x[0, 0] = rand()
    x[0, 1] = rand()

    y[0, 0] = rand()
    y[0, 1] = rand()

    # [0, ... n-2] is for 'warming up'
    # [n-1, ...  -2] = n-1:-1     is for Xt, Yt
    #     [n, .... ,-1] = n:          is for Xt1, Yt1
    # initial?
    for t in range(1, 2 * n):
        x[t, 0] = 1.4 - x[t - 1, 0] ** 2 + 0.3 * x[t - 1, 1]
        y[t, 0] = 1.4 - (gamma * x[t - 1, 0] * y[t - 1, 0] + (1 - gamma) * (y[t - 1, 0] ** 2)) + 0.3 * y[t - 1, 1]

        x[t, 1] = x[t - 1, 0]
        y[t, 1] = y[t - 1, 0]

    Xt1 = x[-n:, :]
    Yt1 = y[-n:, :]
    Xt = x[(-n - 1):-1, :]
    Yt = y[(-n - 1):-1, :]

    assert len(Xt1) == len(Yt1) == len(Xt) == len(Yt) == n
    return (Xt1, Yt, Xt[:, 0:2]) if independence else (Yt1, Xt, Yt[:, 0:2])


def normalize(X):
    return (X - np.mean(X)) / np.std(X)


def zhang2012(seed, N, dimensions, the_case, independent=True):
    np.random.seed(seed)

    assert dimensions > 0
    assert the_case == 1 or the_case == 2

    if the_case == 1:
        X = randn(N, 1)
        Y = randn(N, 1)
        Z = randn(N, 1)
        ZZ1 = 0.7 * ((Z ** 3 / 5) + (Z / 2))
        X = ZZ1 + tanh(X)
        X = X + (X ** 3 / 3) + (tanh(X / 3) / 2)
        ZZ2 = ((Z ** 3 / 4) + Z) / 3
        Y += ZZ2
        Y = Y + tanh(Y / 3)

        X = normalize(X)
        Y = normalize(Y)
        Z = normalize(Z)

        if dimensions > 1:
            noisy_dims = randn(N, dimensions - 1)
            Z = np.hstack([Z, noisy_dims])

    else:
        if dimensions > 5:
            raise Exception('Between 1 and 5 dimensions supported.')
        # % Case II
        X = randn(N, 1)
        Y = randn(N, 1)
        Z = randn(N, 1)
        ZZ1 = 0.7 * ((Z ** 3 / 5) + (Z / 2))
        X = ZZ1 + tanh(X)
        X = X + (X ** 3 / 3) + (tanh(X / 3) / 2)
        ZZ2 = ((Z ** 3 / 4) + Z) / 3
        Y += ZZ2
        Y = Y + tanh(Y / 3)

        X = normalize(X)
        Y = normalize(Y)
        Z = normalize(Z)

        if dimensions > 1:
            Z2 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_2 = (ZZ1 / 2) + Z2
            ZZ1_2 = (ZZ1_2 / 2) + 0.7 * tanh(ZZ1_2)
            X = ZZ1_2 + tanh(X)
            X = X + ((X ** 3) / 3) + tanh(X / 3) / 2
            ZZ2_2 = ZZ2 / 2 + Z2
            ZZ2_2 = ZZ2_2 / 2 + 0.7 * tanh(ZZ2_2)
            Y += ZZ2_2
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z2 = normalize(Z2)
            Z = np.hstack([Z, Z2])

        if dimensions > 2:
            Z3 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_3 = ZZ1_2 * 2 / 3 + Z3 * 5 / 6
            ZZ1_3 = ZZ1_3 / 2 + 0.7 * tanh(ZZ1_3)
            X = ZZ1_3 + tanh(X)
            X = X + (X ** 3) / 3 + tanh(X / 3) / 2
            ZZ2_3 = ZZ2_2 * 2 / 3 + Z3 * 5 / 6
            ZZ2_3 = ZZ2_3 / 2 + 0.7 * tanh(ZZ2_3)
            Y += ZZ2_3
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z3 = normalize(Z3)
            Z = np.hstack([Z, Z3])

        if dimensions > 3:
            Z4 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_4 = ZZ1_3 * 2 / 3 + Z4 * 5 / 6
            ZZ1_4 = ZZ1_4 / 2 + 0.7 * tanh(ZZ1_4)
            X = ZZ1_4 + tanh(X)
            X = X + ((X ** 3) / 3) + tanh(X / 3) / 2
            ZZ2_4 = ZZ2_3 * 2 / 3 + Z4 * 5 / 6
            ZZ2_4 = ZZ2_4 / 2 + 0.7 * tanh(ZZ2_4)
            Y += ZZ2_4
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z4 = normalize(Z4)
            Z = np.hstack([Z, Z4])

        if dimensions > 4:
            Z5 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_5 = ZZ1_4 * 2 / 3 + Z5 * 5 / 6
            ZZ1_5 = ZZ1_5 / 2 + 0.7 * tanh(ZZ1_5)
            X = ZZ1_5 + tanh(X)
            X = X + ((X ** 3) / 3) + tanh(X / 3) / 2
            ZZ2_5 = ZZ2_4 * 2 / 3 + Z5 * 5 / 6
            ZZ2_5 = ZZ2_5 / 2 + 0.7 * tanh(ZZ2_5)
            Y += ZZ2_5
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z5 = normalize(Z5)
            Z = np.hstack([Z, Z5])

    if not independent:
        ff = 0.5 * randn(N, 1)
        X += ff
        Y += ff

    return X, Y, Z


def symmetric_zhang2012(seed, N, dimensions, the_case, independent=True):
    np.random.seed(seed)

    if the_case == 1:
        X = randn(N, 1)
        Y = randn(N, 1)
        Z = randn(N, 1)
        ZZ1 = 0.7 * ((Z ** 3 / 5) + (Z / 2))
        X = ZZ1 + tanh(X)
        X = X + (X ** 3 / 3) + (tanh(X / 3) / 2)
        ZZ2 = ((Z ** 3 / 4) + Z) / 3
        Y += ZZ2
        Y = Y + tanh(Y / 3)

        X = normalize(X)
        Y = normalize(Y)
        Z = normalize(Z)

        if dimensions > 1:
            noisy_dims = randn(N, dimensions - 1)
            Z = np.hstack([Z, noisy_dims])
    else:
        # % Case II
        X = randn(N, 1)
        Y = randn(N, 1)
        Z = randn(N, 1)
        ZZ1 = 0.7 * ((Z ** 3 / 5) + (Z / 2))
        X = ZZ1 + tanh(X)
        X = X + (X ** 3 / 3) + (tanh(X / 3) / 2)
        ZZ2 = ((Z ** 3 / 4) + Z) / 3
        Y += ZZ2
        Y = Y + tanh(Y / 3)

        X = normalize(X)
        Y = normalize(Y)
        Z = normalize(Z)

        if dimensions > 1:
            Z2 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_2 = (ZZ1 / 2) + Z2
            ZZ1_2 = (ZZ1_2 / 2) + 0.7 * tanh(ZZ1_2)
            X = ZZ1_2 + tanh(X)
            X = X + ((X ** 3) / 3) + tanh(X / 3) / 2
            ZZ2_2 = ZZ2 / 2 + Z2
            ZZ2_2 = ZZ2_2 / 2 + 0.7 * tanh(ZZ2_2)
            Y += ZZ2_2
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z2 = normalize(Z2)
            Z = np.hstack([Z, Z2])

        if dimensions > 2:
            Z3 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_3 = ZZ1_2 * 2 / 3 + Z3 * 5 / 6
            ZZ1_3 = ZZ1_3 / 2 + 0.7 * tanh(ZZ1_3)
            X = ZZ1_3 + tanh(X)
            X = X + (X ** 3) / 3 + tanh(X / 3) / 2
            ZZ2_3 = ZZ2_2 * 2 / 3 + Z3 * 5 / 6
            ZZ2_3 = ZZ2_3 / 2 + 0.7 * tanh(ZZ2_3)
            Y += ZZ2_3
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z3 = normalize(Z3)
            Z = np.hstack([Z, Z3])

        if dimensions > 3:
            Z4 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_4 = ZZ1_3 * 2 / 3 + Z4 * 5 / 6
            ZZ1_4 = ZZ1_4 / 2 + 0.7 * tanh(ZZ1_4)
            X = ZZ1_4 + tanh(X)
            X = X + ((X ** 3) / 3) + tanh(X / 3) / 2
            ZZ2_4 = ZZ2_3 * 2 / 3 + Z4 * 5 / 6
            ZZ2_4 = ZZ2_4 / 2 + 0.7 * tanh(ZZ2_4)
            Y += ZZ2_4
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z4 = normalize(Z4)
            Z = np.hstack([Z, Z4])

        if dimensions > 4:
            Z5 = randn(N, 1)
            X = randn(N, 1)
            Y = randn(N, 1)
            ZZ1_5 = ZZ1_4 * 2 / 3 + Z5 * 5 / 6
            ZZ1_5 = ZZ1_5 / 2 + 0.7 * tanh(ZZ1_5)
            X = ZZ1_5 + tanh(X)
            X = X + ((X ** 3) / 3) + tanh(X / 3) / 2
            ZZ2_5 = ZZ2_4 * 2 / 3 + Z5 * 5 / 6
            ZZ2_5 = ZZ2_5 / 2 + 0.7 * tanh(ZZ2_5)
            Y += ZZ2_5
            Y = Y + tanh(Y / 3)

            X = normalize(X)
            Y = normalize(Y)
            Z5 = normalize(Z5)
            Z = np.hstack([Z, Z5])

    ff = 0.5 * randn(N, 1)
    X += ff
    if independent:
        ff = 0.5 * randn(N, 1)
    Y += ff

    return X, Y, Z


if __name__ == '__main__':
    for strindep, indep in [('indep', True), ('dep', False)]:
        X, Y, Z = zhang2012(0, 400, 1, 1, indep)
        import seaborn as sns
        import matplotlib.pyplot as plt

        paper_rc = {'lines.linewidth': 1, 'lines.markersize': 2}
        sns.set_context("paper", rc=paper_rc)
        sns.set(style='white', font_scale=1.4)
        plt.figure(figsize=[3, 3])
        plt.rc('text', usetex=True)
        plt.rc('text.latex', preamble=r'\usepackage{cmbright}')

        # zzz = Z[:, 0]
        # zzz01 = (zzz - zzz.min()) / (zzz.max() - zzz.min())
        plt.scatter(Z[:, 0], Y[:, 0], s=20, alpha=0.5)
        plt.scatter(Z[:, 0], X[:, 0], s=20, alpha=0.5)
        sns.despine()

        if indep:
            plt.axes().set_xlim([-2.5, 2.5])
            plt.axes().set_ylim([-3, 3])
        else:
            plt.axes().set_xlim([-2.5, 2.5])
            plt.axes().set_ylim([-3, 3])
        plt.savefig('zhang_400_{}.pdf'.format(strindep))
        plt.close()


        # for dimm in range(1, 6):
        #     for indep in [True, False]:
        #         for the_case in [1, 2]:
        #             X, Y, Z = zhang2012(0, 200, dimm, the_case, indep)
        #             print(X.shape, Y.shape, Z.shape)
        #
        # x, y, z = henon(0, 1000, 0.5, True)
        # x, y, z = henon(0, 1000, 0.3, False)
        # print(x.shape, y.shape, z.shape)
        # import seaborn as sns
        # import matplotlib.pyplot as plt
        #
        # sns.set()
        # plt.scatter(xt[:, 0], yt[:, 0], s=3, alpha=0.5)
        # plt.savefig('chaotic.pdf')
