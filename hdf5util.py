# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 16:47:51 2014

@author: fanbin
"""
import numpy as np;
from astropy.table import Table
import h5py
import pandas
from astropy.io.misc.hdf5 import write_table_hdf5,read_table_hdf5
import datetime
from bindata import DataHandler

quote_col = ['Open','Close','High','Low','Pre','Vol','Amt']



def WriteToHDF(panel, desp, filename):
    code="";
    f = h5py.File(filename, 'w')
    mt = {"version":"3.0", "CLASS":"TABLE", 
    "TITLE":"quote", "FIELD_0_NAME":"TIMESTAMP",
    "FIELD_1_NAME":"Open","FIELD_2_NAME":"Close",
    "FIELD_3_NAME":"High", "FIELD_4_NAME":"Low","FIELD_5_NAME":"Prev",
    "FIELD_6_NAME":"Vol", "FIELD_7_NAME":"Amt"}
    for tp in panel.iteritems():
        code=tp[0];
        ind = tp[1].index.values
        head=np.matrix((ind.astype('uint64') / 1e6).astype('uint64')).T
        belly=tp[1].as_matrix();
        dt=np.hstack((head,belly))
        col = np.append(['TIMESTAMP'], quote_col)
        dt = dt[~np.isnan(dt).any(axis=1).A1]
        #  ----this line consumes much time, needs optimization
        tb = Table(dt, names=col, meta=mt, dtype=('i8','f4','f4','f4','f4','f4','f4','f4'))
        #  ----
        grp = f.create_group("/stock/"+code)
        write_table_hdf5(table=tb, output=grp, path='quote', overwrite=True)
        grp.attrs['code'] = code
        grp.attrs['name'] = desp[code]['name']
        grp.attrs['gics'] = desp[code]['gics']
        grp.attrs['first']= head[0]
        grp.attrs['last'] = head[-1]
        grp.attrs['beg']= datetime.datetime.utcfromtimestamp(head[0]/1000).strftime('%Y%m%d.%H:%M:%S')
        grp.attrs['end']= datetime.datetime.utcfromtimestamp(head[-1]/1000).strftime('%Y%m%d.%H:%M:%S')
        grp.attrs['nrow']= ind.size
    f.close()
    
    
def ReadFromHDF(filename):
    pn = DataHandler()
    f = h5py.File(filename, 'r')
    
    # read stock data
    rgroup = f['stock']
    
    grps = rgroup.keys();
    for key in grps:
        grp = rgroup[key]
        attrs= grp.attrs
        astro_tb = read_table_hdf5(grp, path='quote')
        m = np.matrix(astro_tb['TIMESTAMP'])
        for i in quote_col:
            t = np.matrix(astro_tb[i])
            m = np.hstack((m,t))
        id = pandas.to_datetime(np.array(m[:,0]).flatten(), unit='ms')
        data=np.array(m[:,1:])
        df=pandas.DataFrame(data, index=id, columns=quote_col)
        pn.stock[key] = df
        pn.code.append(key)
        pn.desp[key] = {}
        pn.desp[key]['gics'] = attrs.get(name='gics')
        pn.desp[key]['name'] = attrs.get(name='name')
    f.close()
    pn.stock = pandas.Panel(pn.stock)
    pn.date = pn.stock.major_axis
    pn.status_table = pandas.DataFrame(index=pn.date, columns=pn.code)
    pn.compile_table()
    return pn 
