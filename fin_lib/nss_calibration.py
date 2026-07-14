import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def nss(t, beta0 = 0.0, beta1 = 0.0, beta2 = 0.0, beta3 = 0.0, tau1 = 1.0, tau2 = 1.0):
        """
        Compute the Nelson-Siegel-Svensson yield curve.

        Parameters
        ----------
        t : array_like
        Maturities (years). Zeros are handled through the analytical limit (1 - exp(-t/tau)) / (t/tau) -> 1 per t -> 0.
        beta0, beta1, beta2, beta3, tau1, tau2 : float
        NSS model's parameters
        """
        t = np.asarray(t, dtype = float)

        with np.errstate(divide="ignore", invalid="ignore"):
                ratio1 = np.where(t == 0, 1.0, (1 - np.exp(-t / tau1)) / (t / tau1))
                ratio2 = np.where(t == 0, 1.0, (1 - np.exp(-t / tau2)) / (t / tau2))

        term1 = beta0
        term2 = beta1 * ratio1
        term3 = beta2 * (ratio1 - np.exp(-t / tau1))
        term4 = beta3 * (ratio2 - np.exp(-t / tau2))
        
        return term1 + term2 + term3 + term4

def calibration_nss(maturities, yields, output_maturities=None, p0=None):
        """
        Calibrates the NSS model on observed data and produces predictions.

        Parameters
        ----------
        maturities : array_like
                Observed maturities.
        yields : array_like
                Observed yields.
        output_maturities : array_like, optional
                Required maturities for predictions. If not specified, inputted 'maturities' will be used.
        p0 : array_like, optional
                Starting values for the 6 parameters [beta0, beta1, beta2, beta3,
                tau1, tau2]. If not specified, a default estimation on observed data will be used.

        Returns
        -------
        output : pd.DataFrame
                DataFrame with columns "Maturities" and "NSS Predictions".
        optimized_params : np.ndarray
                Array of the 6 calibrated parameters [beta0, beta1, beta2, beta3,
                tau1, tau2], useful to reuse the model without a new calibration.
        """
        maturities = np.asarray(maturities, dtype=float)
        yields = np.asarray(yields, dtype=float)

        bounds = (
                [-np.inf, -np.inf, -np.inf, -np.inf, 1e-4, 1e-4],
                [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        )

        if p0 is None:
                p0 = [yields[-1], yields[0] - yields[-1], 0.0, 0.0, 1.0, 5.0]

        optimized_params, _ = curve_fit(
                nss,
                maturities,
                yields,
                p0=p0,
                bounds=bounds,
                maxfev=10000,
        )

        if output_maturities is None or len(output_maturities) == 0:
                output_maturities = maturities

        output = pd.DataFrame({
                "Maturities": output_maturities,
                "NSS Predictions": nss(output_maturities, *optimized_params),
        })

        return output, optimized_params

def display_nss(nss_df: pd.DataFrame, maturities, yields, ax=None, show=True):
        """Display the calibrated NSS curve against the observed data.

        Parameters
        ----------
        nss_df : pd.DataFrame
                DataFrame of NSS curve with columns "Maturities" and "NSS Predictions".
                Output of 'nss()' or 'calibration_nss()
        maturities, yields : array_like
                Observed data.
        ax : matplotlib.axes.Axes, optional
                If specified, plot on this axes instead of creating a new one.
        show : bool
                If True (default), call plt.show(). Disable if you're using the module in a batch/non interactive script.

        Returns
        -------
        fig, ax : used figure and axes, for further customisation.
        """
        if ax is None:
                fig, ax = plt.subplots()
        else:
                fig = ax.figure

        ax.plot(
                nss_df["Maturities"],
                nss_df["NSS Predictions"],
                label="Calibrated NSS Model",
                color="blue",
        )

        ax.scatter(
                maturities,
                yields,
                label="Observed Data",
                color="red",
        )

        ax.legend()
        ax.set_title("NSS Curve Fit")
        ax.set_xlabel("Maturity")
        ax.set_ylabel("Yield")
        fig.tight_layout()

        if show:
                plt.show()

        return fig, ax
        

if __name__ == "__main__":
        sample_maturities = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
        sample_yields = [4.8, 4.7, 4.5, 4.2, 4.0, 3.9, 3.95, 4.1, 4.4, 4.5]

        output_maturities = np.linspace(0.1, 30, 200)

        df, params = calibration_nss(sample_maturities, sample_yields, output_maturities)
        print("Calibrated parameters [beta0, beta1, beta2, beta3, tau1, tau2]:")
        print(params)

        display_nss(df, sample_maturities, sample_yields)