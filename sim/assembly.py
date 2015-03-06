import cPickle

tps = ['anime','book','music','game','real']

bucket=dict()

for tp in tps:
    fr = open('dat/training-'+tp+'.dat','rb')
    S = cPickle.load(fr)
    States = cPickle.load(fr)
    fr.close()
    Stateslil=States.tolil()
    
    fr = open('dat/temp-'+tp+'.dat','rb')
    U = cPickle.load(fr)
    Vt = cPickle.load(fr)
    Bu = cPickle.load(fr)
    Bi = cPickle.load(fr)
    fr.close()

    I,J = States.row, States.col
    for i in xrange(States.getnnz()):
        s = Stateslil[I[i],J[i]]
        if S[I[i],J[i]]==0:
            S[I[i],J[i]]=U[I[i],:].dot(Vt[:,J[i]])+Bu[I[i],s]+Bi[J[i],s]

    bucket[tp]=S

fw = open('dat/assembly.dat','wb')
cPickle.dump(bucket,fw)
fw.close()
