import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from random import shuffle
from sklearn.utils import check_array, check_random_state
import sys
from sklearn.utils.extmath import safe_sparse_dot
from sklearn.utils.fixes import expit


class BangumiMatrixFactorization(BaseEstimator, TransformerMixin):
    """
    Matrix Factorization trained with SGD.
    """
    def __init__(self, U_init, V_init, Ubar_init, Ibar_init, Bu_init, Bi_init, miu,
                n_iter=200, learningrate=0.0002,
                omega=1,
                n_jobs=0, verbose=0):
        self.M=U_init.shape[0]
        self.N=V_init.shape[0]
        self.U=U_init
        self.V=V_init
        self.Ubar=Ubar_init
        self.Ibar=Ibar_init
        self.Bu=Bu_init
        self.Bi=Bi_init
        self.miu=miu
        self.n_iter=n_iter
        self.omega=omega
        self.learningrate=learningrate
        self.verbose=verbose

        self.rmse_train=[]
        self.rmse_validation=[]

    def fit(self, X, y, Xv=None, yv=None):
        """
        param:
        X=array of (user_index, item_index, state_index)
        y=array of rate
        """
        b_validation = Xv is not None
        U=self.U
        V=self.V
        Ubar=self.Ubar
        Ibar=self.Ibar
        Bu=self.Bu

        prevrmse = 0
        for x,rate in zip(X,y):
            i=x[0]
            j=x[1]
            s=x[2]
            drate = rate-U[i,:].dot(V[:,j])-Ubar[i]-Ibar[j]-Bu[i,s]-Bi[j,s]-self.miu;
            prevrmse=prevrmse+drate**2;
        prevrmse=np.sqrt(prevrmse/len(y))
        self.rmse_train.append(prevrmse)
        if b_validation:
            prevrmse = 0
            for x,rate in zip(Xv,yv):
                i=x[0]
                j=x[1]
                s=x[2]
                drate = rate-U[i,:].dot(V[:,j])-Ubar[i]-Ibar[j]-Bu[i,s]-Bi[j,s]-self.miu;
                prevrmse=prevrmse+drate**2;
            prevrmse=np.sqrt(prevrmse/len(yv))
            self.rmse_validation.append(prevrmse)

        if self.verbose:
            print "Start training: train set rmse = %f"%(self.rmse_train[0])
            if b_validation:
                print "\tvalidation set rmse = %f"%self.rmse_validation[0]
        sys.stdout.flush()

        for n in xrange(self.n_iter):
            rmse=0
            t=zip(X,y)
            shuffle(t)
            X,y=zip(*t)
            for x,rate in zip(X,y):
                i=x[0]
                j=x[1]
                s=x[2]
                drate = rate-U[i,:].dot(V[:,j])-Ubar[i]-Ibar[j]-Bu[i,s]-Bi[j,s]-self.miu;
                U[i,:]=U[i,:]+(2*drate*V[:,j].T-2*U[i,:]/self.omega)*self.learningrate;
                V[:,j]=V[:,j]+(2*drate*U[i,:].T-2*V[:,j]/self.omega)*self.learningrate;
                Ubar[i]=Ubar[i]+(2*drate-2*Ubar[i]/self.omega)*self.learningrate;
                Ibar[j]=Ibar[j]+(2*drate-2*Ibar[j]/self.omega)*self.learningrate;
                Bu[i,s]=Bu[i,s]+(2*drate-2*Bu[i,s]/self.omega)*self.learningrate;
                Bi[j,s]=Bi[j,s]+(2*drate-2*Bi[j,s]/self.omega)*self.learningrate;


            for x,rate in zip(X,y):
                i=x[0]
                j=x[1]
                s=x[2]
                drate = rate-U[i,:].dot(V[:,j])-Ubar[i]-Ibar[j]-Bu[i,s]-Bi[j,s]-self.miu;
                rmse=rmse+drate**2;
            rmse=np.sqrt(rmse/len(y))
            self.rmse_train.append(rmse)
            if b_validation:
                for x,rate in zip(Xv,yv):
                    i=x[0]
                    j=x[1]
                    s=x[2]
                    drate = rate-U[i,:].dot(V[:,j])-Ubar[i]-Ibar[j]-Bu[i,s]-Bi[j,s]-self.miu;
                    rmse=rmse+drate**2;
                rmse=np.sqrt(rmse/len(yv))
                self.rmse_validation.append(rmse)

            if self.verbose:
                print "Iteration %d: train set rmse = %f"%(n+1,self.rmse_train[n+1])
                if b_validation:
                    print "\tvalidation set rmse = %f"%self.rmse_validation[n+1]
            if self.rmse_train[n+1]>self.rmse_train[n]:
                print "[WARNING]rmse increased after one round of training."
            if b_validation and self.rmse_validation[n+1]>self.rmse_validation[n]:
                print "[WARNING]rmse increased on validation set."
            sys.stdout.flush()

        self.U=U
        self.V=V
        self.Bu=Bu
        self.Bi=Bi
        self.Ubar=Ubar
        self.Ibar=Ibar
        return self

    def predict(self, X):
        y=[]
        U=self.U
        V=self.V
        Bu=self.Bu
        Bi=self.Bi
        Ubar=self.Ubar
        Ibar=self.Ibar
        for x in X:
            i=x[0]
            j=x[1]
            s=x[2]
            y.append(U[i,:].dot(V[:,j])+Ubar[i]+Ibar[j]+Bu[i,s]+Bi[j,s]+self.miu)
        return y

class BangumiSoftmaxRBM(BaseEstimator):
    def __init__(self, n_components=256, learningrate=0.1, n_randomwalk=1,
                 n_iter=10, verbose=0, random_state=None):
        self.n_components = n_components
        self.learningrate = learningrate
        self.n_iter = n_iter
        self.verbose = verbose
        self.random_state = random_state
        self.n_randomwalk=n_randomwalk

        self.rng = check_random_state(self.random_state)
        self.rmse = []

    def _sample_hiddens(self, v, W, rng):
        """v: dense matrix. (nV,K)
        return: binarized hidden nodes, following p(h=1|v)
        """
        h = self._prob_hiddens(v, W)
        return (rng.random_sample(size=h.shape) < h).astype(int)

    def _prob_visibles(self, h, W, mask = None):
        """h: dense array (nH,1)
        return the softmax prob of V
        """
        if mask is not None:
            v = self.intercept_visible_[mask,:]
        else:
            v = self.intercept_visible_
        for i in xrange(h.shape[0]):
            v += W[i,:,:]
        expit(v,out=v)
        for i in xrange(v.shape[0]):
            v[i,:]/=sum(v[i,:])
        return v;

    def _prob_hiddens(self, v, W):
        """v: dense matrix. (nV,K)
        returns: p(h=1|v)
        """
        w = W.reshape((W.shape[0], W.shape[1]*W.shape[2]))
        h = w.dot(np.ravel(v))# shape: (nH,)
        h += self.intercept_hidden_
        expit(h,out=h)
        return h

    def _fit(self, v_pos, rng, n_samples):
        """x is a training sample
        we call it v
        typical dimensions of v_pos: nV*K
        typical dimensions of h: nH*1
        typical dimensions of W: nH*nV*K
        """
        mask_item=v_pos.nonzero()[0]
        v_pos = v_pos[mask_item,:].todense()
        W = self.components_[:, mask_item, :]
        hprob_pos = self._prob_hiddens(v_pos, W)
        h_pos = (rng.random_sample(size=hprob_pos.shape) < hprob_pos).astype(int)

        for i in xrange(self.n_randomwalk-1):
            v_neg = self._prob_visibles(h_pos, W, mask_item) # p(v=1|h), prob
            h_pos = self._sample_hiddens(v_neg, W, rng)  # p(h=1|v), binary
        v_neg = self._prob_visibles(h_pos, W, mask_item) # p(v=1|h), prob
        hprob_neg = self._prob_hiddens(v_neg, W)

        lr = float(self.learningrate) / n_samples # can use more accurate methods
        update = np.empty((W.shape[0], W.shape[1]*W.shape[2]))
        update = np.outer(np.ravel(hprob_pos), np.ravel(v_pos))-\
                 np.outer(np.ravel(hprob_neg), np.ravel(v_neg));
        update = np.reshape(update, (W.shape))
        self.components_[:,mask_item,:]+=lr*update
        self.intercept_hidden_ += lr*(hprob_pos-hprob_neg)
        self.intercept_visible_[mask_item,:] += lr*(v_pos-v_neg)

    def _rmse(self, X, rng):
        K=X[0].shape[1]
        cnt=0;
        rtn=0;
        for x in X:
            cnt+=x.getnnz()
            mask_item = x.nonzero()[0]
            v = x[mask_item,:].todense()
            h = self._sample_hiddens(v, self.components_[:,mask_item,:], rng)
            v = self._prob_visibles(h, self.components_[:,mask_item,:], mask_item)
            v = v.dot(np.arange(1,K+1))
            rate = x.nonzero()[1]+1;
            rtn += np.sum((rate-v)**2)
        return np.sqrt(rtn/cnt)

    def fit(self, X, y=None):
        """X: training samples.
        list of a user's movie records.
        it should be a sparse matrix, with first dimension equals
        number of items, and second dimension equals number of possible
        ratings.
        """
        n_samples = len(X)
        nV = X[0].shape[0]
        K = X[0].shape[1]
        rng = self.rng

        self.components_ = np.asarray(
            rng.normal(0, 0.01, (self.n_components, nV, K)))
        self.intercept_hidden_ = np.zeros((self.n_components, ))
        self.intercept_visible_ = np.zeros((nV,K))

        for iteration in xrange(1, self.n_iter + 1):
            # as you can see, it's sgd
            shuffle(X)
            for i in xrange(len(X)):
                self._fit(X[i],rng,n_samples)
            # record
            t=self._rmse(X, rng)
            self.rmse.append(t)

            if self.verbose:
                print("[%s] Iteration %d, rmse on training set = %.2f"
                    %(type(self).__name__, iteration,
                    self.rmse[-1]))
                sys.stdout.flush()
        return self

    def predict(self, x, item_mask=None):
        x = check_array(x, accept_sparse='csr', dtype=np.float)
        nV = x.shape[0]
        K = x.shape[1]
        mask_item=x.nonzero()[0]
        x = x[mask_item,:].todense()
        h = self._sample_hiddens(x, self.components_[:,mask_item,:], self.rng)
        if item_mask is not None:
            v = self._prob_visibles(h, self.components_[:,item_mask,:], item_mask)
        else:
            v = self._prob_visibles(h, self.components_)
        return np.dot(v,np.arange(1,K+1))
