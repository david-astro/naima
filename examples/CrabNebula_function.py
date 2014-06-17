#!/usr/bin/env python
import numpy as np
import gammafit
import astropy.units as u
from astropy.io import ascii

## Read data

data=ascii.read('CrabNebula_HESS_2006.dat')

## Set initial parameters

p0=np.array((1.5e-12,2.4,np.log10(15.0),))
labels=['norm','index','log10(cutoff)']

## Model definition

def cutoffexp(pars,data):
    """
    Powerlaw with exponential cutoff

    Parameters:
        - 0: PL normalization
        - 1: PL index
        - 2: log10(cutoff energy)
    """

    ene=data['ene']
    # take logarithmic mean of first and last data points as normalization
    # energy (reasonable approximation of decorrelation energy for gamma~2)
    ene0=np.sqrt(ene[0]*ene[-1])

    N     = pars[0]
    gamma = pars[1]
    ecut  = (10**pars[2])*u.TeV

    return N*(ene/ene0)**-gamma*np.exp(-(ene/ecut)) * data['flux'].unit

## Prior definition

def lnprior(pars):
	"""
	Return probability of parameter values according to prior knowledge.
	Parameter limits should be done here through uniform prior ditributions
	"""

	logprob = gammafit.uniform_prior(pars[0],0.,np.inf) \
            + gammafit.uniform_prior(pars[1],-1,5)

	return logprob

if __name__=='__main__':
## Run sampler

    sampler,pos = gammafit.run_sampler(data_table=data, p0=p0, labels=labels,
            model=cutoffexp, prior=lnprior, nwalkers=128, nburn=50, nrun=10,
            threads=4)

## Save sampler
    from astropy.extern import six
    from six.moves import cPickle
    sampler.pool=None
    cPickle.dump(sampler,open('CrabNebula_function_sampler.pickle','wb'))

## Diagnostic plots
    gammafit.generate_diagnostic_plots('CrabNebula_function',sampler,
            sed=True,last_step=False)

