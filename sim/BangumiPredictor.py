import numpy as np
from sklearn.base import BaseEstimator
from random import shuffle
import sys


class BangumiMatrixFactorization(BaseEstimator):
    """
    Matrix Factorization trained with SGD.
    """
    def __init__(self, U_init, V_init, Bu_init, Bi_init, miu,
                n_iter=100, learningrate=0.0002,
                omega=1,
                n_jobs=0, verbose=0):
        self.M=U_init.shape[0]
        self.N=V_init.shape[0]
        self.U=U_init
        self.V=V_init
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
        Bu=self.Bu
        Bi=self.Bi
        miu=self.miu
        omega=self.omega
        learningrate = self.learningrate
        verbose=self.verbose

        prevrmse = 0
        for x,rate in zip(X,y):
            i=x[0]
            j=x[1]
            s=x[2]
            drate = rate-U[i,:].dot(V[:,j])-Bu[i,s]-Bi[j,s]-miu;
            prevrmse=prevrmse+drate**2;
        prevrmse=np.sqrt(prevrmse/len(y))
        self.rmse_train.append(prevrmse)
        if b_validation:
            prevrmse = 0
            for x,rate in zip(Xv,yv):
                i=x[0]
                j=x[1]
                s=x[2]
                drate = rate-U[i,:].dot(V[:,j])-Bu[i,s]-Bi[j,s]-miu;
                prevrmse=prevrmse+drate**2;
            prevrmse=np.sqrt(prevrmse/len(yv))
            self.rmse_validation.append(prevrmse)

        if verbose:
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
                drate = rate-U[i,:].dot(V[:,j])-Bu[i,s]-Bi[j,s]-miu;
                U[i,:]=U[i,:]+(2*drate*V[:,j].T-2*U[i,:]/omega)*learningrate;
                V[:,j]=V[:,j]+(2*drate*U[i,:].T-2*V[:,j]/omega)*learningrate;
                Bu[i,s]=Bu[i,s]+(2*drate-2*Bu[i,s]/omega)*learningrate;
                Bi[j,s]=Bi[j,s]+(2*drate-2*Bi[j,s]/omega)*learningrate;

            for x,rate in zip(X,y):
                i=x[0]
                j=x[1]
                s=x[2]
                drate = rate-U[i,:].dot(V[:,j])-Bu[i,s]-Bi[j,s]-miu;
                rmse=rmse+drate**2;
            rmse=np.sqrt(rmse/len(y))
            self.rmse_train.append(rmse)
            if b_validation:
                for x,rate in zip(Xv,yv):
                    i=x[0]
                    j=x[1]
                    s=x[2]
                    drate = rate-U[i,:].dot(V[:,j])-Bu[i,s]-Bi[j,s]-miu;
                    rmse=rmse+drate**2;
                rmse=np.sqrt(rmse/len(yv))
                self.rmse_validation.append(rmse)

            if verbose:
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

    def predict(self, X):
        y=[]
        U=self.U
        V=self.V
        Bu=self.Bu
        Bi=self.Bi
        for x in X:
            i=x[0]
            j=x[1]
            s=x[2]
            y.append(U[i,:].dot(V[:,j])+Bu[i,s]+Bi[j,s]+miu)
        return y
