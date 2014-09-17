# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 16:47:51 2014

@author: fanbin
"""
import numpy as np;
import h5py

def WriteToHDF(panel, filename):
    code="";
    store = h5py.File(filename,'w')
    for tp in panel.iteritems():
        code=tp[0];
        ind = tp[1].index.values
        head=np.matrix((ind.astype('uint64') / 1e6).astype('uint64')).T
        col = np.append(['date'], tp[1].columns.values)
        belly=tp[1].as_matrix();
        dt=np.hstack((head,belly))
        store.create_dataset(code, data=dt)
    
    store.close()
