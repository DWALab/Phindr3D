# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of src <https://github.com/DWALab/Phindr3D>.
#
# src is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# src is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with src.  If not, see <http://www.gnu.org/licenses/>.

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import pairwise_distances
from scipy.spatial.distance import cdist
import numpy as np
from src.GUI.windows.helperclasses import *
from PyQt5.QtWidgets import *
import matplotlib
from kneed import KneeLocator
import scipy as sc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

class clusterdisplay(object):
    def __init__(self, x, y, xp, yp, win_title, xlabel, ylabel, opt_label, text, num):
        #main layout
        win = QDialog()
        win.setWindowTitle(win_title)
        win.setLayout(QGridLayout())
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="2d")
        if num==0:
            sc_plot = self.main_plot.axes.plot(x, y, 'r--')
            self.main_plot.axes.set_title(win_title)
            self.main_plot.axes.set_xlabel(xlabel)
            self.main_plot.axes.set_ylabel(ylabel)
        else:
            sc_plot=self.main_plot.axes.plot(x, y, '-r', label='# Clusters')
            sc_plot=self.main_plot.axes.plot(xp, yp, 'bo', label='Optimal Cluster')
            # axis/title labels
            self.main_plot.axes.set_title(win_title)
            self.main_plot.axes.set_xlabel(xlabel)
            self.main_plot.axes.set_ylabel(ylabel)
            self.main_plot.axes.text(text[0], text[1], text[2])
            self.main_plot.axes.legend()
        self.main_plot.draw()
        toolbar = NavigationToolbar(self.main_plot, win)
        win.layout().addWidget(toolbar)
        win.layout().addWidget(self.main_plot)
        win.show()
        win.exec()

class Clustering:
    def __init__(self):
        self.eps = np.finfo(np.float64).eps
        self.realmin = np.finfo(np.float64).tiny
        self.realmax = np.finfo(np.float64).max

    def plot_type(self, X, dim, plot):

        if plot == "PCA":
            func = 'linear'
            sc = StandardScaler()
            X_show = sc.fit_transform(X)
            pca = KernelPCA(n_components=dim, kernel=func)
            P = pca.fit(X_show).transform(X_show)
            return ('PCA plot', 'PCA 1', 'PCA 2', P)
        elif plot == "t-SNE":
            T = TSNE(n_components=dim, init='pca', learning_rate='auto').fit_transform(X)
            return ('t-SNE plot', 't-SNE 1', 't-SNE 2', T)
        elif plot == "Sammon":
            S, E = self.sammon(self, X, dim)
            return ('Sammon plot', 'Sammon 1', 'Sammon 2', S)
        else:
            raise Exception("Invalid plot")

    def clusterest(self, X):
        eps = np.finfo(np.float64).eps
        realmin = np.finfo(np.float64).tiny
        realmax = np.finfo(np.float64).max
        self.estimateNumClusters(self, X)

    """Static methods for cluster analysis. Referenced from
    https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
    and
    https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
    No constructor. All parameters and methods are static.
    """
    @staticmethod
    def cmdscale(D):
        # copied from https://github.com/tompollard/sammon as no other python libraries appear to have implemented sammon mapping.

        """
        Classical multidimensional scaling (MDS)

        Parameters
        ----------
        D : (n, n) array
            Symmetric distance matrix.

        Returns
        -------
        Y : (n, p) array
            Configuration matrix. Each column represents a dimension. Only the
            p dimensions corresponding to positive eigenvalues of B are returned.
            Note that each dimension is only determined up to an overall sign,
            corresponding to a reflection.

        e : (n,) array
            Eigenvalues of B.

        """
        # Number of points
        n = len(D)

        # Centering matrix
        H = np.eye(n) - np.ones((n, n)) / n

        # YY^T
        B = -H.dot(D ** 2).dot(H) / 2

        # Diagonalize
        evals, evecs = np.linalg.eigh(B)

        # Sort by eigenvalue in descending order
        idx = np.argsort(evals)[::-1]
        evals = evals[idx]
        evecs = evecs[:, idx]

        # Compute the coordinates using positive-eigenvalued components only
        w, = np.where(evals > 0)
        L = np.diag(np.sqrt(evals[w]))
        V = evecs[:, w]
        Y = V.dot(L)

        return Y, evals[evals > 0]

    @staticmethod
    def rescale(x, newmin=0, newmax=1):
        """
        This function linearly rescales an array to the range [newmin, newmax]
        :param x:, numpy array, to be rescaled
        :param newmin: float, minimum value in new range
        :param newmax: float, maximum value in new range

        :return: x rescaled.
        """
        minx = np.min(x)
        maxx = np.max(x)
        return (x - minx) / (maxx - minx) * (newmax - newmin) + newmin

    @staticmethod
    def sammon(self, x, n, display=0, inputdist='raw', maxhalves=20, maxiter=500, tolfun=1e-9, init='default'):
        # copied from https://github.com/tompollard/sammon as no other python libraries appear to have implemented sammon mapping.
        # this appears to be the same implementation as is used in matlab's drtoolbox.

        """Perform Sammon mapping on dataset x
        y = sammon(x) applies the Sammon nonlinear mapping procedure on
        multivariate data x, where each row represents a pattern and each column
        represents a feature.  On completion, y contains the corresponding
        co-ordinates of each point on the map.  By default, a two-dimensional
        map is created.  Note if x contains any duplicated rows, SAMMON will
        fail (ungracefully).
        [y,E] = sammon(x) also returns the value of the cost function in E (i.e.
        the stress of the mapping).
        An N-dimensional output map is generated by y = sammon(x,n) .
        A set of optimisation options can be specified using optional
        arguments, y = sammon(x,n,[OPTS]):
           maxiter        - maximum number of iterations
           tolfun         - relative tolerance on objective function
           maxhalves      - maximum number of step halvings
           input          - {'raw','distance'} if set to 'distance', X is
                            interpreted as a matrix of pairwise distances.
           display        - 0 to 2. 0 least verbose, 2 max verbose.
           init           - {'pca', 'cmdscale', random', 'default'}
                            default is 'pca' if input is 'raw',
                            'msdcale' if input is 'distance'
        The default options are retrieved by calling sammon(x) with no
        parameters.
        File        : sammon.py
        Date        : 18 April 2014
        Authors     : Tom J. Pollard (tom.pollard.11@ucl.ac.uk)
                    : Ported from MATLAB implementation by
                      Gavin C. Cawley and Nicola L. C. Talbot
        Description : Simple python implementation of Sammon's non-linear
                      mapping algorithm [1].
        References  : [1] Sammon, John W. Jr., "A Nonlinear Mapping for Data
                      Structure Analysis", IEEE Transactions on Computers,
                      vol. C-18, no. 5, pp 401-409, May 1969.
        Copyright   : (c) Dr Gavin C. Cawley, November 2007.
        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 2 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program; if not, write to the Free Software
        Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
        """

        # Create distance matrix unless given by parameters
        if x.shape[0] > 10000:
            raise ValueError("should be a memory error actually: input array too big, would cause memory error")
        if inputdist == 'distance':
            D = x
            if init == 'default':
                init = 'cmdscale'
        else:
            D = cdist(x, x)
            if init == 'default':
                init = 'pca'

        if inputdist == 'distance' and init == 'pca':
            raise ValueError("Cannot use init == 'pca' when inputdist == 'distance'")

        if np.count_nonzero(np.diagonal(D)) > 0:
            raise ValueError("The diagonal of the dissimilarity matrix must be zero")

        # Remaining initialisation
        N = x.shape[0]
        scale = 0.5 / D.sum()
        D = D + np.eye(N)

        if np.count_nonzero(D <= 0) > 0:
            raise ValueError("Off-diagonal dissimilarities must be strictly positive")

        Dinv = 1 / D
        if init == 'pca':
            [UU, DD, _] = np.linalg.svd(x)
            y = UU[:, :n] * DD[:n]
        elif init == 'cmdscale':
            y, e = self.cmdscale(D)
            y = y[:, :n]
        else:
            y = np.random.normal(0.0, 1.0, [N, n])
        one = np.ones([N, n])
        d = cdist(y, y) + np.eye(N)
        dinv = 1. / d
        delta = D - d
        E = ((delta ** 2) * Dinv).sum()

        # Get on with it
        for i in range(maxiter):

            # Compute gradient, Hessian and search direction (note it is actually
            # 1/4 of the gradient and Hessian, but the step size is just the ratio
            # of the gradient and the diagonal of the Hessian so it doesn't
            # matter).
            delta = dinv - Dinv
            deltaone = np.dot(delta, one)
            g = np.dot(delta, y) - (y * deltaone)
            dinv3 = dinv ** 3
            y2 = y ** 2
            H = np.dot(dinv3, y2) - deltaone - np.dot(2, y) * np.dot(dinv3, y) + y2 * np.dot(dinv3, one)
            s = -g.flatten(order='F') / np.abs(H.flatten(order='F'))
            y_old = y

            # Use step-halving procedure to ensure progress is made
            for j in range(maxhalves):
                s_reshape = np.reshape(s, (-1, n), order='F')
                y = y_old + s_reshape
                d = cdist(y, y) + np.eye(N)
                dinv = 1 / d
                delta = D - d
                E_new = ((delta ** 2) * Dinv).sum()
                if E_new < E:
                    break
                else:
                    s = 0.5 * s

            # Bomb out if too many halving steps are required
            if j == maxhalves - 1:
                print('Warning: maxhalves exceeded. Sammon mapping may not converge...')

            # Evaluate termination criterion
            if abs((E - E_new) / E) < tolfun:
                if display:
                    print('TolFun exceeded: Optimisation terminated')
                break

            # Report progress
            E = E_new
            if display > 1:
                print('epoch = %d : E = %12.10f' % (i + 1, E * scale))

        if i == maxiter - 1:
            print('Warning: maxiter exceeded. Sammon mapping may not have converged...')

        # Fiddle stress to match the original Sammon paper
        E = E * scale

        return [y, E]

    class C_class:
        """
        a data structure used in the clsIn function.
        """

        def __init__(self):
            self.minClsSize = 5
            self.maxCls = 10
            self.minCls = 1
            self.S = []
            self.pmin = 0
            self.pmax = 0
            self.pmed = 0

    @staticmethod
    def preferenceRange(self, s, method='bound'):
        """called in clsIn"""
        """in third party/clustering folder"""
        """
        % Given a set of similarities, s, this function computes a lower
        % bound, pmin, on the value for the preference where the optimal
        % number of clusters (exemplars) changes from 1 to 2, and the
        % exact value of the preference, pmax, where the optimal
        % number of clusters changes from n-1 to n.
        %
        % For N data points, there may be as many as N^2-N pair-wise
        % similarities (note that the similarity of data point i to k
        % need not be equal to the similarity of data point k to i).
        % These may be passed in an NxN matrix of similarities, s, where
        % s(i,k) is the similarity of point i to point k. In fact, only
        % a smaller number of relevant similarities need to be provided,
        % in which case the others are assumed to be -Inf. M similarity
        % values are known, can be passed in an Mx3 matrix s, where each
        % row of s contains a pair of data point indices and a
        % corresponding similarity value: s(j,3) is the similarity of
        % data point s(j,1) to data point s(j,2).
        %
        % A single-cluster solution may not exist, in which case pmin is
        % set to NaN.
        %
        % [pmin,pmax]=preferenceRange(s,METHOD) uses one of the methods
        % below to compute pmin and pmax:
        %
        %   'exact'      Computes the exact values for pmin and pmax
        %                (Warning: This can be quite slow)
        %
        %   'bound'      Computes the exact value for pmax, but estimates
        %                pmin using a bound (default)
        %
        % Copyright (c) Brendan J. Frey and Delbert Dueck (2007). This
        % software may be freely used and distributed for
        % non-commercial purposes.
        """

        if len(s.shape) != 2:
            print('\nError: s shuld be a 2d matrix\n')
            return None
        elif s.shape[1] == 3:
            N = np.maximum(np.max(s[:, 0]), np.max(s[:, 1]))
            if np.minimum(np.min(s[:, 0]), np.min(s[:, 1])) < 0:
                print('\nError: data point indices must be >= 0')
                return None
        elif s.shape[0] == s.shape[1]:
            N = s.shape[0]
        else:
            print('\nError: s must have 3 colummns or be square\n')
            return None
        # construct similarity matrix:
        if s.shape[1] == 3:
            S = np.full((N, N), -np.inf)
            for j in range(s.shape[0]):
                S[s[j, 0], s[j, 1]] = s[j, 2]
        else:
            S = s.copy()
        for k in range(N):
            S[k, k] = 0
        # find pmin
        dpsim1 = np.max(np.sum(S, axis=0))
        k11 = np.argmax(np.sum(S, axis=0))
        if dpsim1 == -np.inf:
            pmin = np.nan
        elif method == 'bound':
            for k in range(N):
                S[k, k] = -np.inf
            m = np.max(S, axis=1)
            tmp = np.sum(m, axis=0)
            yy = np.min(m, axis=0)
            ii = np.argmin(m, axis=0)
            tmp = tmp - yy - np.min(np.concatenate((m[:ii], m[ii + 1:N])))
            pmin = dpsim1 - tmp
        elif method == 'exact':
            dpsim2 = -np.inf
            for j21 in range(N - 1):
                for j22 in range(j21, N):
                    tmp = np.sum(np.max(S[:, (j21, j22)]), axis=1)  # poor indexing. probably wont work
                    if tmp > dpsim2:
                        dpsim2 = tmp
                        k21 = j21
                        k22 = j22
            pmin = dpsim1 - dpsim2
        else:
            print('\nError: please properly specify method from "bound" or "exact"\n')
        # find pmax
        for k in range(N):
            S[k, k] = -np.inf
            pmax = np.max(S)
        return pmin, pmax

    ''' #unused? 
    # computeClustering.m
    def computeClustering(data, numberClusters, type='AP', sparse=False, maxits=500, convits=15, dampfact=0.5,
                          plot=False, details=False, nonoise=False):
        print('ran')
        type = type.upper()
        C = clsIn(data)
        print(C.pmed)
        if type == 'AP':
            clusterResult = apclusterK(C.S, numberClusters)
        elif type == 'SK':
            print(C.pmed)
            clusterResult = apcluster_sklearn(data, numberClusters, sparse=sparse, maxits=maxits, convits=convits,
                                              dampfact=dampfact, plot=plot, details=details, nonoise=nonoise)
        else:
            clusterResult = np.arange(0, data.shape[0])
        return clusterResult
    '''

    @staticmethod
    def clsIn(self, data, beta=0.05, dis='euclidean'):
        """
        dis can be: "euclidean" OR "cosine" OR "hamming"
        """

        dis = dis.lower()
        if data.size == 0:  # check if data is empty array
            print('Data is empty')
            return None
        C = self.C_class()
        C.minClsSize = 5
        C.maxCls = 10
        C.minCls = 1
        C.S = []
        C.pmin = 0
        C.pmax = 0
        C.pmed = 0
        sim=pairwise_distances(data, data, metric='euclidean')
        #sim = sc.spatial.distance.cdist(data, data, metric=dis)
        if dis == 'euclidean':
            sim = -1 * sim
        elif (dis == 'cosine') or (sim == 'hamming'):
            sim = 1 - sim
        x_x = np.tril(np.ones((sim.shape[0], sim.shape[0]), dtype=bool),
                      -1)  # lower triangular matrix True below the diagonal, false elsewhere.
        C.pmed = np.median(sim[
                               x_x])  # i think this is the right axis, but very unsure. Should be median along rows of 2d matrix since sim[x_x] is 2d matrix however, numpy rows and cols are different than in matlab.
        C.pmin, C.pmax = self.preferenceRange(self, sim)
        C.S = sim  # similarity matrix
        return C

    @staticmethod
    def apcluster_sparse(self, s, p, maxits=500, convits=50, dampfact=0.5, plot=False, details=False,
                         nonoise=False):  # plot=False, details=False, nonoise=False):
        """
        %
        % APCLUSTER uses affinity propagation (Frey and Dueck, Science,
        % 2007) to identify data clusters, using a set of real-valued
        % pair-wise data point similarities as input. Each cluster is
        % represented by a data point called a cluster center, and the
        % method searches for clusters so as to maximize a fitness
        % function called net similarity. The method is iterative and
        % stops after maxits iterations (default of 500 - see below for
        % how to change this value) or when the cluster centers stay
        % constant for convits iterations (default of 50). The command
        % apcluster(s,p,'plot') can be used to plot the net similarity
        % during operation of the algorithm.
        %
        % For N data points, there may be as many as N^2-N pair-wise
        % similarities (note that the similarity of data point i to k
        % need not be equal to the similarity of data point k to i).
        % These may be passed to APCLUSTER in an NxN matrix s, where
        % s(i,k) is the similarity of point i to point k. In fact, only
        % a smaller number of relevant similarities are needed for
        % APCLUSTER to work. If only M similarity values are known,
        % where M < N^2-N, they can be passed to APCLUSTER in an Mx3
        % matrix s, where each row of s contains a pair of data point
        % indices and a corresponding similarity value: s(j,3) is the
        % similarity of data point s(j,1) to data point s(j,2).
        %
        % APCLUSTER automatically determines the number of clusters,
        % based on the input p, which is an Nx1 matrix of real numbers
        % called preferences. p(i) indicates the preference that data
        % point i be chosen as a cluster center. A good choice is to
        % set all preference values to the median of the similarity
        % values. The number of identified clusters can be increased or
        % decreased  by changing this value accordingly. If p is a
        % scalar, APCLUSTER assumes all preferences are equal to p.
        %
        % The fitness function (net similarity) used to search for
        % solutions equals the sum of the preferences of the the data
        % centers plus the sum of the similarities of the other data
        % points to their data centers.
        %
        % The identified cluster centers and the assignments of other
        % data points to these centers are returned in idx. idx(j) is
        % the index of the data point that is the cluster center for
        % data point j. If idx(j) equals j, then point j is itself a
        % cluster center. The sum of the similarities of the data
        % points to their cluster centers is returned in dpsim, the
        % sum of the preferences of the identified cluster centers is
        % returned in expref and the net similarity (sum of the data
        % point similarities and preferences) is returned in netsim.
        %
        % EXAMPLE
        %
        % N=100; x=rand(N,2); % Create N, 2-D data points
        % M=N*N-N; s=zeros(M,3); % Make ALL N^2-N similarities
        % j=1;
        % for i=1:N
        %   for k=[1:i-1,i+1:N]
        %     s(j,1)=i; s(j,2)=k; s(j,3)=-sum((x(i,:)-x(k,:)).^2);
        %     j=j+1;
        %   end;
        % end;
        % p=median(s(:,3)); % Set preference to median similarity
        % [idx,netsim,dpsim,expref]=apcluster(s,p,'plot');
        % fprintf('Number of clusters: %d\n',length(unique(idx)));
        % fprintf('Fitness (net similarity): %f\n',netsim);
        % figure; % Make a figures showing the data and the clusters
        % for i=unique(idx)'
        %   ii=find(idx==i); h=plot(x(ii,1),x(ii,2),'o'); hold on;
        %   col=rand(1,3); set(h,'Color',col,'MarkerFaceColor',col);
        %   xi1=x(i,1)*ones(size(ii)); xi2=x(i,2)*ones(size(ii));
        %   line([x(ii,1),xi1]',[x(ii,2),xi2]','Color',col);
        % end;
        % axis equal tight;
        %
        % PARAMETERS
        %
        % [idx,netsim,dpsim,expref]=apcluster(s,p,'NAME',VALUE,...)
        %
        % The following parameters can be set by providing name-value
        % pairs, eg, apcluster(s,p,'maxits',1000):
        %
        %   Parameter    Value
        %   'sparse'     No value needed. Use when the number of data
        %                points is large (eg, >3000). Normally,
        %                APCLUSTER passes messages between every pair
        %                of data points. This flag causes APCLUSTER
        %                to pass messages between pairs of points only
        %                if their input similarity is provided and
        %                is not equal to -Inf.
        %   'maxits'     Any positive integer. This specifies the
        %                maximum number of iterations performed by
        %                affinity propagation. Default: 500.
        %   'convits'    Any positive integer. APCLUSTER decides that
        %                the algorithm has converged if the estimated
        %                cluster centers stay fixed for convits
        %                iterations. Increase this value to apply a
        %                more stringent convergence test. Default: 50.
        %   'dampfact'   A real number that is less than 1 and
        %                greater than or equal to 0.5. This sets the
        %                damping level of the message-passing method,
        %                where values close to 1 correspond to heavy
        %                damping which may be needed if oscillations
        %                occur.
        %   'plot'       No value needed. This creates a figure that
        %                plots the net similarity after each iteration
        %                of the method. If the net similarity fails to
        %                converge, consider increasing the values of
        %                dampfact and maxits.
        %   'details'    No value needed. This causes idx, netsim,
        %                dpsim and expref to be stored after each
        %                iteration.
        %   'nonoise'    No value needed. Degenerate input similarities
        %                (eg, where the similarity of i to k equals the
        %                similarity of k to i) can prevent convergence.
        %                To avoid this, APCLUSTER adds a small amount
        %                of noise to the input similarities. This flag
        %                turns off the addition of noise.
        %
        % Copyright (c) Brendan J. Frey and Delbert Dueck (2006). This
        % software may be freely used and distributed for
        % non-commercial purposes.
        """
        maxits = int(maxits)
        if maxits <= 0:
            print('maxits must be positve integer')
            return None
        convits = int(convits)
        if convits <= 0:
            print('convits must be positive integer')
            return None
        lam = dampfact
        if (lam < 0.5) or (lam >= 1):
            print('dampfact must be in the range [0.5, 1)')
            return None
        if lam > 0.9:
            print(
                '\nLarge damping factor selected, plotting is recommended, Algorithm will also change decisions slowly so large convits should be set as well.\n')
        if len(s.shape) != 2:
            print('s should be 2d matrix')
            return None
        elif len(p.shape) > 2:
            print('p should be vector or scalar')
        elif s.shape[1] == 3:
            tmp = np.maximum(np.max(s[:, 0]), np.max(s[:, 1]))
            if len(p) == 1:
                N = tmp
            else:
                N = len(p)
            if tmp > N:
                print('Error, data point index exceeds number of datapoints')
                return None
            elif np.minimum(np.min(s[:, 0]), np.min(s[:, 1])) < 0:
                print('Error, indices must be >= 0')
                return None
        else:
            print('Error, s must have 3 columns or be square.')
            return None

            # make vector of preferences:
        if len(p) == 1:
            p = p * np.ones(N, 1)
        # append any self-similarities (preferences) to s-matrix
        tmps = np.concatenate((np.tile(np.arange(0, N).T, [0, 1]), p))
        s = np.concatenate((s, tmps))
        M = s.shape[0]
        if not nonoise:
            rns = np.random.get_state()
            np.random.seed(0)
            s[:, 2] = s[:, 2] + (self.eps * s[:, 2] + self.realmin * 100) * np.random.random((M, 1))
            np.random.set_state(rns)
        # construct indices of neighbors:
        ind1e = np.zeros((N, 1))
        for j in range(M):
            k = s[j, 0]
            ind1e[k] = ind1e[k] + 1
        ind1e = np.sum(ind1e)
        ind1s = np.concatenate((1, ind1e[:-1] + 1))
        ind1 = np.zeros(M, 1)
        for j in range(M):
            k = s[j, 0]
            ind1[ind1s[k]] = j
            ind1s[k] = ind1s[k] + 1
        ind1s = np.concatenate((1, ind1e[:-1] + 1))
        ind2e = np.zeros(N, 1)
        for j in range(M):
            k = s[j, 1]
            ind2e[k] = ind2e[k] + 1
        ind2e = np.sum(ind2e)
        ind2s = np.concatenate((1, ind2e[:-1] + 1))
        ind2 = np.zeros((M, 1))
        for j in range(M):
            k = s[j, 1]
            ind2[ind2s[k]] = j
            ind2s[k] = ind2s[k] + 1
        ind2s = np.concatenate((1, ind2e[:-1] + 1))
        # allocate space for messages, etc:
        A = np.zeros((M, 1))
        R = np.zeros((M, 1))
        t = 1
        if plot:
            netsim = np.zeros((1, maxits + 1))
        if details:
            idx = np.zeros((N, maxits + 1))
            netsim = np.zeros((N, maxits + 1))
            dpsim = np.zeros((N, maxits + 1))
            expref = np.zeros((N, maxits + 1))
        # execute parallel affinity propagation updates:
        e = np.zeros((N, convits))
        dn = False
        i = 0
        while not dn:
            i += 1
            # compute responsibilities:
            for j in range(N):
                ss = s[ind1s[j]:ind1e[j], 2]
                As = A[ind1s[j]:ind1e[j]] + ss
                Y = np.amax(As, axis=0)
                I = np.argmin(As, axis=0)
                As[I] = -self.realmax
                Y2 = np.amax(As, axis=0)
                I2 = np.argmax(As, axis=0)
                r = ss - Y
                r[I] = ss[I] - Y2
                R[ind1[ind1s[j]:ind1e[j]]] = (1 - lam) * r + lam * R[ind1[ind1s[j]:ind1e[j]]]
            # compute availabilities:
            for j in range(N):
                rp = R[ind2[ind2s[j]:ind2e[j]]]
                rp[:-1] = np.maximum(rp[:-1])
                a = np.sum(rp, axis=0) - rp
                a[:-1] = np.minimum(a[:-1], 0)
                A[ind2[ind2s[j]:ind2e[j]]] = (1 - lam) * a + lam * A[ind2[ind2s[j]:ind2e[j]]]
            # check for convergence:
            E = ((A[M - N:M] + R[M - N:M]) > 0)
            e[:, ((i - 1) % convits) + 1] = E
            K = np.sum(E, axis=0)
            if i >= convits or i >= maxits:
                se = np.sum(e, axis=1)
                unconverged = (np.sum((se == convits) + (se == 0)) != N)
                if (not unconverged and (K > 0)) or (i == maxits):
                    dn = True

            # handle plotting and detail storage if required.
            if plot or details:
                if k == 0:
                    tmpnetsim = np.nan
                    tmpdpsim = np.nan
                    tmpexpref = np.nan
                    tmpidx = np.nan
                else:
                    tmpidx = np.zeros((N, 1))
                    tmpdsim = 0
                    tmpidx[np.nonzero(E)] = np.nonzero(E)
                    tmpexpref = np.sum(p[np.nonzero(E)])
                    discon = False
                    for j in np.where(E == 0):
                        ss = s[ind1[ind1s[j]:ind1e[j]], 2]
                        ii = s[ind1[ind1s[j]:ind1e[j]], 1]
                        ee = np.nonzero(E[ii])
                        if len(ee) == 0:
                            discon = True
                        else:
                            smx = np.max(ss[ee])
                            imx = np.argmax(ss[ee])
                            tmpidx[j] = ii[ee[imx]]
                            tmpdpsim += smx
                    if discon:
                        tmpnetsim = np.nan
                        tmpdpsim = np.nan
                        tmpexpref = np.nan
                        tmpidx = np.nan
                    else:
                        tmpnetsim = tmpdpsim + tmpexpref
            if details:
                netsim[i] = tmpnetsim
                dpsim[i] = tmpdpsim
                expref[i] = tmpexpref
                idx[:, i] = tmpidx
            if plot:
                netsim[i] = tmpnetsim
                tmp = np.arrange(0, i)
                tmpi = np.nonzero(np.isfinite(netsim[:i]))
                # matplotlib
                matplotlib.use('Qt5Agg')
                winc = clusterdisplay(tmp[tmpi], netsim[tmpi], None, None, 'ap_cluster_sparse' '# iterations',
                                      'Net similarity of quantized intermediate solutions', None, None, 0)
        # identify exemplars
        E = ((A[M - N:M] + R[M - N:M]) > 0)
        K = np.sum(E)
        if K > 0:
            tmpidx = np.zeros((N, 1))
            tmpidx[np.nonzero(E)] = np.nonzero[E]  # identify clusters
            for j in np.nonzero(E == 0).T:
                ss = s[ind1[ind1[j]:ind1e[j]], 2]
                ii = s[ind1[ind1[j]:ind1e[j]], 1]
                ee = np.nonzero(E[ii])
                smx = np.max(ss[ee])
                imx = np.argmax([ss[ee]])
                tmpidx[j] = ii[ee[imx]]
            EE = np.zeros((N, 1))
            for j in np.nonzero(E).T:
                jj = np.nonzero(tmpidx == j)
                mx = -np.inf  # this doesnt get used
                ns = np.zeros((N, 1))
                msk = p.zeros((N, 1))
                for m in jj.T:
                    mm = s[ind1[ind1s[m]:ind1e[m]], 1]
                    msk[mm] = msk[mm] + 1
                    ns[mm] = ns[mm] + s[ind1[ind1s[m]:ind1e[m]], 2]
                ii = jj[np.nonzero(msk[jj] == len(jj))]
                smx = np.max(ns[ii])
                imx = np.argmax(ns[ii])
                EE[ii[imx]] = 1
            E = EE
            tmpidx = np.zeros((N, 1))
            tmpdpsiim = 0
            tmpidx[np.nonzero(E)] = np.nonzero(E)
            tmpexpref = np.sum(p[np.nonzero(E)])
            for j in np.nonzero(E == 0).T:
                ss = s[ind1[ind1s[j]:ind1e[j]], 2]
                ii = s[ind1[ind1s[j]:ind1e[j]], 1]
                ee = np.nonzero(E[ii])
                smx = np.max(ss[ee])
                imx = np.argmax(ss[ee])
                tmpidx[j] = ii[ee[imx]]
                tmpdpsim = tmpdpsim + smx
            tmpnetsim = tmpdpsim + tmpexpref
        else:
            tmpidx = np.full((N, 1), np.nan)
            tmpnetsim = np.nan
            tmpexpref = np.nan
        if details:
            netsim[i + 1] = tmpnetsim
            netsim = netsim[:i + 1]
            dpsim[i + 1] = tmpnetsim - tmpexpref
            dpsim = dpsim[:i + 1]
            expref[i + 1] = tmpexpref
            expref = expref[:i + 1]
            idx[:, i + 1] = tmpidx
            idx = idx[:, :i + 1]
        else:
            netsim = tmpnetsim
            dpsim = tmpnetsim - tmpexpref
            expref = tmpexpref
            idx = tmpidx
        if plot or details:
            print(f'\nNUmber of identified clusters: {K}')
            print(f'Fitness (net similarity): {tmpnetsim}')
            print(f'\tSimilarities of data points to exemplars: {dpsim[-1]}')
            print(f'\tPreferences of selected exemplars: {tmpexpref}')
            print(f'Number of iterations: {i}')
        if unconverged:
            print(f'\n*** Warning: Algorithm did not converger. The similarities may contain degeneracies.')
            print(
                f'\tAdd noise to similarities to remove degeneracies. To monitor thhe similarity, activate plotting.')
            print(f'also consider increasing maxits and if necessary dampfact')
        return idx, netsim, dpsim, expref

    # https://www.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/14620/versions/4/previews/apcluster.m/index.html
    # https://www.mathworks.com/matlabcentral/fileexchange/25722-fast-affinity-propagation-clustering-under-given-number-of-clusters?tab=discussions
    @staticmethod
    def apcluster(self, s, p, sparse=False, maxits=500, convits=50, dampfact=0.5, plot=False, details=False,
                  nonoise=False):  # maxits=500,convits=50, dampfact=0.5,  plot=False, details=False,nonoise=False):
        """in third party/clustering"""
        """
        s = similarities
        p = preferences
        % APCLUSTER uses affinity propagation (Frey and Dueck, Science,
        % 2007) to identify data clusters, using a set of real-valued
        % pair-wise data point similarities as input. Each cluster is
        % represented by a data point called a cluster center, and the
        % method searches for clusters so as to maximize a fitness
        % function called net similarity. The method is iterative and
        % stops after maxits iterations (default of 500 - see below for
        % how to change this value) or when the cluster centers stay
        % constant for convits iterations (default of 50). The command
        % apcluster(s,p,'plot') can be used to plot the net similarity
        % during operation of the algorithm.
        %
        % For N data points, there may be as many as N^2-N pair-wise
        % similarities (note that the similarity of data point i to k
        % need not be equal to the similarity of data point k to i).
        % These may be passed to APCLUSTER in an NxN matrix s, where
        % s(i,k) is the similarity of point i to point k. In fact, only
        % a smaller number of relevant similarities are needed for
        % APCLUSTER to work. If only M similarity values are known,
        % where M < N^2-N, they can be passed to APCLUSTER in an Mx3
        % matrix s, where each row of s contains a pair of data point
        % indices and a corresponding similarity value: s(j,3) is the
        % similarity of data point s(j,1) to data point s(j,2).
        %
        % APCLUSTER automatically determines the number of clusters,
        % based on the input p, which is an Nx1 matrix of real numbers
        % called preferences. p(i) indicates the preference that data
        % point i be chosen as a cluster center. A good choice is to 
        % set all preference values to the median of the similarity
        % values. The number of identified clusters can be increased or
        % decreased  by changing this value accordingly. If p is a
        % scalar, APCLUSTER assumes all preferences are equal to p.
        %
        % The fitness function (net similarity) used to search for
        % solutions equals the sum of the preferences of the the data
        % centers plus the sum of the similarities of the other data
        % points to their data centers.
        %
        % The identified cluster centers and the assignments of other
        % data points to these centers are returned in idx. idx(j) is
        % the index of the data point that is the cluster center for
        % data point j. If idx(j) equals j, then point j is itself a
        % cluster center. The sum of the similarities of the data
        % points to their cluster centers is returned in dpsim, the
        % sum of the preferences of the identified cluster centers is
        % returned in expref and the net similarity (sum of the data
        % point similarities and preferences) is returned in netsim.
        %
        % EXAMPLE
        %
        % N=100; x=rand(N,2); % Create N, 2-D data points
        % M=N*N-N; s=zeros(M,3); % Make ALL N^2-N similarities
        % j=1;
        % for i=1:N
        %   for k=[1:i-1,i+1:N]
        %     s(j,1)=i; s(j,2)=k; s(j,3)=-sum((x(i,:)-x(k,:)).^2);
        %     j=j+1;
        %   end;
        % end;
        % p=median(s(:,3)); % Set preference to median similarity
        % [idx,netsim,dpsim,expref]=apcluster(s,p,'plot');
        % fprintf('Number of clusters: %d\n',length(unique(idx)));
        % fprintf('Fitness (net similarity): %f\n',netsim);
        % figure; % Make a figures showing the data and the clusters
        % for i=unique(idx)'
        %   ii=find(idx==i); h=plot(x(ii,1),x(ii,2),'o'); hold on;
        %   col=rand(1,3); set(h,'Color',col,'MarkerFaceColor',col);
        %   xi1=x(i,1)*ones(size(ii)); xi2=x(i,2)*ones(size(ii)); 
        %   line([x(ii,1),xi1]',[x(ii,2),xi2]','Color',col);
        % end;
        % axis equal tight;
        %
        % PARAMETERS
        % 
        % [idx,netsim,dpsim,expref]=apcluster(s,p,'NAME',VALUE,...)
        % 
        % The following parameters can be set by providing name-value
        % pairs, eg, apcluster(s,p,'maxits',1000):
        %
        %   Parameter    Value
        %   'sparse'     No value needed. Use when the number of data
        %                points is large (eg, >3000). Normally,
        %                APCLUSTER passes messages between every pair
        %                of data points. This flag causes APCLUSTER
        %                to pass messages between pairs of points only
        %                if their input similarity is provided and
        %                is not equal to -Inf.
        %   'maxits'     Any positive integer. This specifies the
        %                maximum number of iterations performed by
        %                affinity propagation. Default: 500.
        %   'convits'    Any positive integer. APCLUSTER decides that
        %                the algorithm has converged if the estimated
        %                cluster centers stay fixed for convits
        %                iterations. Increase this value to apply a
        %                more stringent convergence test. Default: 50.
        %   'dampfact'   A real number that is less than 1 and
        %                greater than or equal to 0.5. This sets the
        %                damping level of the message-passing method,
        %                where values close to 1 correspond to heavy
        %                damping which may be needed if oscillations
        %                occur.
        %   'plot'       No value needed. This creates a figure that
        %                plots the net similarity after each iteration
        %                of the method. If the net similarity fails to
        %                converge, consider increasing the values of
        %                dampfact and maxits.
        %   'details'    No value needed. This causes idx, netsim,
        %                dpsim and expref to be stored after each
        %                iteration.
        %   'nonoise'    No value needed. Degenerate input similarities
        %                (eg, where the similarity of i to k equals the
        %                similarity of k to i) can prevent convergence.
        %                To avoid this, APCLUSTER adds a small amount
        %                of noise to the input similarities. This flag
        %                turns off the addition of noise.
        %
        % Copyright (c) Brendan J. Frey and Delbert Dueck (2006). This
        % software may be freely used and distributed for
        % non-commercial purposes.
        """
        ##Global R, A, E, tmpidx, tmpnetsim, S #These get define later down, BUT maybe only behind an if statement.
        ##check inputs
        if sparse == True:
            return self.apcluster_sparse(s, p, maxits=maxits, convits=convits, dampfact=dampfact, plot=plot,
                                    details=details, nonoise=nonoise)
        maxits = int(maxits)
        if maxits <= 0:
            print('maxits must be positve integer')
            return None
        convits = int(convits)
        if convits <= 0:
            print('convits must be positive integer')
            return None
        lam = dampfact
        if (lam < 0.5) or (lam >= 1):
            print('dampfact must be in the range [0.5, 1)')
            return None
        if lam > 0.9:
            print(
                '\nLarge damping factor selected, plotting is recommended, Algorithm will also change decisions slowly so large convits should be set as well.\n')
        if len(s.shape) != 2:
            print('s should be 2d matrix')
            return None
        elif len(p.shape) > 2:
            print('p should be vector or scalar')
        elif s.shape[1] == 3:
            tmp = np.maximum(np.max(s[:, 0]), np.max(s[:, 1]))
            if len(p) == 1:
                N = tmp
            else:
                N = len(p)
            if tmp > N:
                print('Error, data point index exceeds number of datapoints')
                return None
            elif np.minimum(np.min(s[:, 0]), np.min(s[:, 1])) < 0:
                print('Error, indices must be >= 0')
                return None
        elif s.shape[0] == s.shape[1]:
            N = s.shape[0]
            if (np.array([p]).size != N) and (not np.isscalar(p)):
                print('Error, p should be scalar or vector of size N')
                return None
        else:
            print('Error, s must have 3 columns or be square.')
            return None
            # construct similarity matrix
        if N > 3000:
            print('\nLarge memory request, consider setting sparse=True\n')
        if s.shape[1] == 3:  # make square similarity matrix
            S = np.full((N, N), -np.inf)
            for j in range(0, s.shape[0]):
                S[s[j, 0], s[j, 1]] = s[j, 3]
        else:
            S = s.copy()
        # in case user did not remove degeneracies from input similarities, avoid degenerate solutions by adding small noise to input similarities
        if not nonoise:
            rns = np.random.get_state()
            np.random.seed(0)
            S = S + (self.eps * S + self.realmin * 100) * np.random.random(
                (N, N))  # (eps*S+realmin*100) is orginial form (probably too small to make a difference)
            np.random.set_state(rns)
        # place preference on diagonal of S
        if np.isscalar(p):
            for i in range(N):
                S[i, i] = p
        else:
            for i in range(N):
                S[i, i] = p[i]
        # make place for messages, etc:
        dS = np.diag(S)
        A = np.zeros((N, N))
        R = np.zeros((N, N))
        t = 1
        if plot:
            netsim = np.zeros(maxits + 1)
        if details:
            idx = np.zeros((N, maxits + 1))
            netsim = np.zeros(maxits + 1)
            dpsim = np.zeros(maxits + 1)
            expref = np.zeros(maxits + 1)

        # execute parallel affinity propagation updates!
        e = np.zeros((N, convits))
        dn = False
        i = 0
        while not dn:
            i += 1
            # compute responsibilities
            Rold = R.copy()
            AS = A + S
            Y = np.amax(AS, axis=1)
            I = np.argmax(AS, axis=1)  # have to remember that I is along axis 1
            for k in range(N):
                AS[k, I[k]] = -self.realmax
            Y2 = np.amax(AS, axis=1)
            I2 = np.argmax(AS, axis=1)
            R = S - np.tile(Y, [N, 1])
            for k in range(N):
                R[k, I[k]] = S[k, I[k]] - Y2[k]
            # damping
            R = (1 - lam) * R + lam * Rold

            # compute availabilities
            Aold = A.copy()
            Rp = np.maximum(R, 0)
            for k in range(N):
                Rp[k, k] = R[k, k]
            A = np.tile(np.sum(Rp, axis=0), [N, 1]) - Rp
            dA = np.diag(A)
            A = np.minimum(A, 0)
            for k in range(N):
                A[k, k] = dA[k]
            # damping
            A = (1 - lam) * A + lam * Aold
            # check for convergence
            E = ((np.diag(A) + np.diag(R)) > 0)
            e[:, (i - 1) % convits] = E
            K = np.sum(E)  # I think E is a vector so sum should work properly
            if i >= convits or i >= maxits:
                se = np.sum(e, axis=1)
                unconverged = (np.sum((se == convits) + (se == 0)) != N)
                if (not unconverged and (K > 0)) or (i == maxits):
                    dn = True
            # handle plotting/details storage
            if plot or details:
                if K == 0:
                    tmpnetsim = np.nan;
                    tmpdpsim = np.nan;
                    tmpexpref = np.nan;
                    tmpidx = np.nan
                else:
                    I = np.nonzero(E)
                    tmp = np.amax(S[:, I], axis=1)
                    c = np.argmax(S[:, I], axis=1)
                    c[I] = np.arange(0, K)
                    tmpidx = I[c]
                    tmpnetsim = np.sum(S[(tmpidx - 1) * N + np.arange[0, N].T], axis=0)  # might not need axis here
                    tmpexpref = np.sum(dS[I])
                    tmpdpsim = tmpnetsim - tmpexpref
            if details:
                netsim[i] = tmpnetsim
                dpsim[i] = tmpdpsim
                expref[i] = tmpexpref
                idx[:, i] = tmpidx
            if plot:
                netsim[i] = tmpnetsim
                tmp = np.arange(0, i)
                tmpi = np.nonzero(np.isfinite(netsim[:i]))
                # replace matplotlib
                matplotlib.use('Qt5Agg')
                winc = clusterdisplay(tmp[tmpi], netsim[tmpi], None, None, 'apcluster', '# iterations',
                                      'Fitness (net similarity) of quantized intermediate solution', None, None, 0)
        # identify exemplars
        I = np.nonzero(np.diag(A + R) > 0)[0]  # non-zero returns a tuple: (array of indices, type)
        K = max(I.shape)  # fixed len to matlab "Length"
        if K > 0:
            # identify clusters
            tmp = np.amax(S[:, I], axis=1)  # all rows, columns from I, max along column axis
            c = np.argmax(S[:, I], axis=1)  # index of maximum along axis()
            c[I] = np.arange(0, K)
            # refine the final set of exemplars and clusters and return results
            for k in range(K):
                ii = np.nonzero(c == k)[0]
                # y = np.max(np.sum(S[ii, ii], axis=0))
                j = np.argmax(np.sum(S[ii, ii], axis=0))
                I[k] = ii[j]
            tmp = np.amax(S[:, I], axis=1)
            c = np.argmax(S[:, I], axis=1)
            c[I] = np.arange(0, K)
            tmpidx = I[c]  # choose I's based on c
            flat = S.ravel()  # for linear indexing in next line
            tmpnetsim = np.sum(
                flat[(tmpidx) * N + np.arange(0, N)])  # this formula is for linear indices #possibly wrong
            tmpexpref = np.sum(dS[I])
        else:
            tmpidx = np.full((N, 1), np.nan)
            tmpnetsim = np.nan
            tmpexpref = np.nan
        if details:
            netsim[i + 1] = tmpnetsim
            netsim = netsim[:i + 1]
            dpsim[i + 1] = tmpnetsim - tmpexpref
            dpsim = dpsim[:i + 1]
            expref[i + 1] = tmpexpref
            expref = expref[:i + 1]
            idx[:, i + 1] = tmpidx
            idx = idx[:, :i + 1]
        else:
            netsim = tmpnetsim
            dpsim = tmpnetsim - tmpexpref
            expref = tmpexpref
            idx = tmpidx
        if plot or details:
            print(f'number of identified clusters: {K}')
            print(f'Fitness (net similarity): {tmpnetsim}')
            print(f'\t similarities of data points to exemplars: {dpsim[-1]}')
            print(f'\t preferences of selected exemplars: {tmpexpref}')
            print(f'number of itereations: {i}\n')
        if unconverged:
            print(
                'algorithm did not converge, similarities may contain degeneracies - add noise to similarities to remove degeneracies.')
            print(
                'To monitor net similarity, activate plotting. Also consider increasing maxits and if necessary, dampfact.')
        return idx, netsim, dpsim, expref, unconverged

    @staticmethod
    def estimateNumClusters(self, X):
        C = self.clsIn(self, X)  # make similarity matrix
        step = 100
        pref = np.linspace(C.pmin, C.pmax, 100, endpoint=True)
        yCls = np.zeros(pref.shape)
        for i in range(len(pref)):
            idx, netsim, dpsim, expref, unconverged = self.apcluster(self, C.S, pref[i], dampfact=0.9)
            uIdx = np.unique(idx)
            if (len(uIdx) == len(idx)) and (i < len(pref)):
                if i == 0:
                    yCls[i] = 1
                else:
                    yCls[i] = yCls[i - 1]
            else:
                yCls[i] = len(uIdx)
        numclust = self.getBestPreference(pref, yCls, pl=True)
        print(f'Estimated optimal number of clusters: {numclust}')

    #   getBestPreference.m
    @staticmethod
    def getBestPreference(x, y, pl=True):
        """
        % %getBestPreference Perform knee point detection
        % to get the best clusters
        % "Knee Point Detection in BIC for Detecting the Number of Clusters"
        % Input:
        %       x - X axis values
        %       y - y axis values
        %       pl - toggle plotting option
        """
        yp = 0  # i think that these are supposed to be indices, so i set to 0. if not, then it should be 1
        xp = np.argwhere(y == 1)
        if x.shape[0] != y.shape[0]:
            print('Error')
            return None
        ys = y
        pp = 3
        maxabd = np.abs(y[2:] + y[0:-2] - (2 * y[1:-1]))
        ix = np.zeros(maxabd.shape[0], dtype=int)
        uMaxabd = np.unique(maxabd)[::-1]  # sort the array in descending order
        uMaxabd = uMaxabd[1:]
        cnt = 0
        for i in range(0, uMaxabd.size):
            ii = np.argwhere(maxabd == uMaxabd[i])[:,
                 0]  # want 1d array of indices, but argwhere returns nx1 array of indices (each in own col.)
            ix[cnt:cnt + ii.size] = ii[np.argsort(-ii)]
            cnt += ii.size
        n = x.size // 20
        ix = ix[0:n]
        ix = ix + 1  # +1 here is a bit sus. I don't know what it does, but the code seems to work with it.
        mangle = np.zeros(n)
        for i in range(0, n):
            if ix[i] > 1:
                sl1 = np.divide((y[ix[i]] - y[ix[i] - 1]), (x[ix[i]] - x[
                    ix[i] - 1]))  # pretty sure this is right. we should be doing proper matrix division
                sl2 = np.divide((y[ix[i] + 1] - y[ix[i]]), (x[ix[i] + 1] - x[ix[i]]))  # same here.
                mangle[i] = np.arctan(np.abs((sl1 + sl2) / (1 - (sl1 * sl2))))
        maxMangle = np.max(mangle)
        uI = (mangle == maxMangle)
        im = np.min(ix[uI])
        ii = im - 2
        xp = x[ii]
        yp = ys[ii]
        y = ys
        # plotting here
        if pl:
            xCent = np.min(x) + 0.1 * (np.max(x) - np.min(x)) / 2
            yCent = np.min(y) + (np.max(y) - np.min(y)) / 2
            optText = f'Estimated Optimal Cluster -- {yp}'

            # matplotlib
            matplotlib.use('Qt5Agg')
            winc = clusterdisplay(x, y, xp, yp, 'Cluster Estimation', 'Preference',
                                  '# Clusters', 'Optimal Cluster', [xCent, yCent, optText], 1)
        return yp
    # end ClusteringFunctions
'''
def plot_type(X, dim, plot):

    if plot=="PCA":
        func='linear'
        sc = StandardScaler()
        X_show = sc.fit_transform(X)
        pca = KernelPCA(n_components=dim, kernel=func)
        P = pca.fit(X_show).transform(X_show)
        return('PCA plot', 'PCA 1', 'PCA 2', P)
    elif plot =="t-SNE":
        T = TSNE(n_components=dim, init='pca', learning_rate='auto').fit_transform(X)
        return('t-SNE plot', 't-SNE 1', 't-SNE 2', T)
    elif plot =="Sammon":
        S, E = Clustering.sammon(X, dim)
        return('Sammon plot', 'Sammon 1', 'Sammon 2', S)
    else:
        raise Exception("Invalid plot")

def clusterest(X):
    eps = np.finfo(np.float64).eps
    realmin = np.finfo(np.float64).tiny
    realmax = np.finfo(np.float64).max
    Clustering.estimateNumClusters(X)
'''
# end class ClusterStuff
if __name__ == '__main__':
    """Not sure what this will do yet"""

    pass





# end main