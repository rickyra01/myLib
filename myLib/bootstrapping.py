import numpy as np

def short_df(rates, maturities):
    """
    Compute the discount factors from short-rates.
    
    Parameters
    ----------
    
    rates: array_like
        Observed short-rates.
    maturities: array_like
        Observed maturities.
    """

    if len(maturities) != len(rates):
        raise ValueError("Maturities and rates must be of same length!")
    
    rates = np.asarray(rates, dtype=float)
    maturities = np.asarray(maturities, dtype=float)

    return np.ones(len(maturities)) / (np.ones(len(maturities)) + rates * maturities)

def bootstrap_df(swap_rates, maturities, period = 1):
    """
    Bootstrap the zcb curve from a given dataset of swap rates.

    Parameters
    ----------

    swap_rates: array_like
        Observed swap rates.
    maturities: array_like 
        Observed maturities.
    period = 1: float
        Number of payments in a year
    """

    if len(maturities) != len(swap_rates):
        raise ValueError("Maturities and rates must be of same length!")
    
    swap_rates = np.asarray(swap_rates, dtype=float)
    maturities = np.asarray(maturities, dtype=float)

    df = []

    if maturities[0] <= 1:
        short_maturities = np.asarray([t for t in maturities if t <= 1])
        short_rates = swap_rates[:len(short_maturities)]
        df.extend(short_df(short_rates, short_maturities))
        update = maturities > 1
        maturities = maturities[update]
        swap_rates = swap_rates[update]

    coupon_leg_sum = 0
    for i in range(len(maturities)):
        coupon_leg_sum += df[- 1] * 1/period
        df.append((1 - (swap_rates[i]*coupon_leg_sum)) / (1 + swap_rates[i]))
    
    return np.asarray(df, dtype=float)

if __name__ == '__main__':
    sample_maturities = [0.08, 0.25, 0.5, 0.75, 1, 2, 3]
    sample_rates = [0.025, 0.026, 0.031, 0.031, 0.032, 0.028, 0.026]

    df = bootstrap_df(sample_rates, sample_maturities)
    print(df)