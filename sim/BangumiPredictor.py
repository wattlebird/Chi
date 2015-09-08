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

class BangumiSoftmaxRBM(BaseEstimator, TransformerMixin):
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
        self.rmsev = []

    def _sample_hiddens(self, v, rng, mask_item):
        """v: dense matrix. (nV,K)
        return: binarized hidden nodes, following p(h=1|v)
        """
        w = self.components_[:,mask_item,:]
        h = np.empty((1,self.n_components))
        for i in xrange(self.K):
            h+=safe_sparse_dot(v[:,i].T, w[i,:,:])
        h += self.intercept_hidden_
        expit(h,out=h)
        return (rng.random_sample(size=h.shape) < p)

    def _prob_visibles(self, h, mask_item):
        """h: dense array (1, nH)
        return the softmax prob of V
        """
        w = self.components_[:,mask_item,:] #(K,nitem,nH)
        v = np.dot(w,h.T)[:,:,0].T #(nitem, K)
        v += self.intercept_visible_[mask_item,:] # (nV, K)
        expit(v,out=v)
        for i in v.shape[0]:
            v[i,:]/=sum(v[i,:])
        return v;

    def _prob_hiddens(self, v, mask_item):
        """v: dense matrix. (nV,K)
        returns: p(h=1|v)
        """
        w = self.components_[:,mask_item,:]
        h = np.empty((1,self.n_components))
        for i in xrange(self.K):
            h+=safe_sparse_dot(v[:,i].T, w[i,:,:])
        h += self.intercept_hidden_
        expit(h,out=h)
        return h

    def _fit(self, v_pos, rng, n_samples):
        """x is a training sample
        we call it v
        typical dimensions of v_pos: nV*K
        typical dimensions of h: 1*nH
        typical dimensions of W: K*nV*nH
        """
        mask_item=v_pos.nonzero()[0]
        v_pos=v_pos[mask_item,:].todense()
        for i in xrange(self.n_randomwalk-1):
            h_pos = self._sample_hiddens(v_pos, rng) # p(h=1|v), binary
            v_pos = self._prob_visibles(h_pos) # p(v=1|h), prob
        h_neg = self._prob_hiddens(v_pos, rng) # p(h=1|v), prob
        v_neg = self._prob_visibles(h_neg) # p(v=1|h), prob

        lr = float(self.learning_rate) / n_samples
        update = np.empty((v_pos.shape[1],v_pos.shape[0],h_pos.shape[1]))
        for i in xrange(update.shape[0]):
            update[i]=np.outer(v_pos[:,i],h_pos)
            update[i]-=np.outer(v_neg[:,i],h_neg)
        self.components_[:,mask_item,:]+=lr*update
        self.intercept_hidden_ += lr*(h_pos-h_neg)
        self.intercept_visible_[mask_item,:] += lr*(v_pos-v_neg)

    def _rmse(self, X, Xv=None):
        if Xv is None:
            cnt=0;
            rtn=0;
            for x in X:
                cnt+=x.getnnz()
                mask_item = x.nonzero()[0]
                v = self.predict(x)[mask_item,:]
                rate = x.nonzero()[1]+1;
                pred = v.dot(np.arange(1,11))
                rtn += np.sum((pred-rate)**2)
            return np.sqrt(rtn/cnt)
        else:
            cnt=0;cntv=0;
            rtn=0;rtnv=0;
            for x,xv in zip(X,Xv):
                cnt+=x.getnnz()
                cntv+=xv.getnnz()
                mask_item = x.nonzero()[0]
                mask_item_v = xv.nonzero()[0]
                v = self.predict(x)
                vt = v[mask_item,:]
                vv = v[mask_item_v,:]
                rate = x.nonzero()[1]+1;
                ratev = x.nonzero()[1]+1;
                pred = vt.dot(np.arange(1,11))
                predv = vv.dot(np.arange(1,11))
                rtn += np.sum((pred-rate)**2)
                rtnv += np.sum((predv-ratev)**2)
            return [np.sqrt(rtn/cnt), np.sqrt(rtnv/cntv)]

    def fit(self, X, y=None, Xv=None):
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
            rng.normal(0, 0.01, (K, nV, self.n_components)))
        self.intercept_hidden_ = np.zeros((1,self.n_components))
        self.intercept_visible_ = np.zeros((nV,K))


        begin = time.time()
        for iteration in xrange(1, self.n_iter + 1):
            if Xv is None:
                shuffle(X)
            else:
                X = zip(X,Xv)
                shuffle(X)
                X,Xv = zip(*X)

            for i in xrange(len(X))
                self._fit(X[i],rng,n_samples)

            t=self._rmse(X,Xv)
            if Xv is not None:
                self.rmsev.append(t[1])
                self.rmse.append(t[0])
            else:
                self.rmse.append(t)

            if self.verbose:
                print("[%s] Iteration %d, rmse on training set = %.2f"
                      % (type(self).__name__, iteration,
                         self.rmse[-1]))
                if Xv is not None:
                    print("rmse on validation set = %.2f"
                    %self.rmsev[-1])

        return self

    def predict(self, x):
        nV = x.shape[0]
        mask_item=x.nonzero()[0]
        x = x[mask_item,:].todense()
        h = self._prob_hiddens(x, mask_item)
        v = self._prob_visibles(h,np.ones((nV,)))
        return v

    def transform(self, x):
        check_is_fitted(self, "components_")
        x = check_array(x, accept_sparse='csr', dtype=np.float)
        mask_item=x.nonzero()[0]
        v = x[mask_item,:]
        h = self._prob_hiddens(v)
        return self._prob_visibles(h, np.ones(X[0].shape[0]))
