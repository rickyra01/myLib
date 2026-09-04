import numpy as np
import pandas as pd
from scipy.optimize import brentq

def survival_probs(hazard_rates, times):
    '''
    Computes survival probabilities from piece constant hazard rates using the formula:
    q(t) = exp(-∫λ(s) ds) from 0 to t

    Parameters
    ----------

    hazard_rates : array-like
        Array of hazard rates at each time point
    times : array-like
        Array of time points

    Returns
    -------

    q : list
        List of survival probabilities at each time point
    '''

    if np.any(np.isnan(hazard_rates)):
        raise ValueError("Invalid hazard curve: contains NaN values.")

    q = [1.0]
    for i in range(len(times)):
        dt = times[i] - (times[i-1] if i > 0 else 0.0)
        q.append(q[-1] * np.exp(-hazard_rates[i] * dt))
    
    return q[1:]

def _cds_equation(lamb, known_lambdas, times, discount_factors, spread, recovery_rate):
        """Computes CDS pricing equation (premium - protection leg)"""     

        lambdas = known_lambdas + [lamb]
        q = survival_probs(lambdas, times)

        premium_leg = 0.0
        protection_leg = 0.0

        for i, t in enumerate(times):
            dt = t - (times[i-1] if i > 0 else 0.0)
            df = discount_factors[t]

            premium_leg += spread * df * q[i] * dt

            q_prev = q[i-1] if i > 0 else 1.0
            protection_leg += (1 - recovery_rate) * df * (q_prev - q[i])

        return premium_leg - protection_leg

def calibrate_hazard_curve(maturities, spreads, discount_factors, recovery_rate = 0.4, bracket = (1e-6, 5.0)):


    maturities = np.asarray(maturities, dtype=float)
    spreads = np.asarray(spreads, dtype=float)

    if len(maturities) != len(spreads):
        raise ValueError("Maturities and spreads must be of same length!")

    hazard_rates = []

    for i, t in enumerate(maturities):
        times = maturities[:i + 1]
        spread = spreads[i]

        try:
            lam = brentq(
                _cds_equation,
                a=bracket[0],
                b=bracket[1],
                args=(hazard_rates, times, discount_factors, spread, recovery_rate),
                maxiter=200
            )
        except ValueError as e:
            raise RuntimeError(
                f"Root finding failed at maturity {t}."
                "Check spreads / discount factors / initial curve."
            )
        
        hazard_rates.append(lam)

    return hazard_rates

if __name__ == "__main__":
    maturities = [ 0.5 , 1.,   2.,   3.,   4.,   5.,   7.,  10.,  20.,  30. ]
    spreads = [0.002413, 0.003028, 0.004080,0.005123,0.006190,0.007259,0.008503,0.009567,.010692,.011557]  # Example spreads in decimal form
    discount_factors = {0.5: 0.987824531640339, 1.0: 0.9771546327005731, 2.0: 0.9548311762081919, 3.0: 0.9333357972395782, 4.0: 0.9118329657622845, 5.0: 0.8901761791245326, 7.0:0.8465788121300368, 10.0: 0.78254238612877, 20.0: 0.6110119248549508, 30.0: 0.3493012842405857}  # Example discount factors

    calibrated_hazard_rates = calibrate_hazard_curve(maturities, spreads, discount_factors)
    print("Calibrated Hazard Rates:", calibrated_hazard_rates)