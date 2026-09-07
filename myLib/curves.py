import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

class NSS():

        """Nelson-Siegel-Svensson yield curve model.

        Attributes
        ----------
        params_ : np.ndarray or None
                Calibrated parameters, available after calling fit().
        cov_matrix_ : np.ndarray or None
                Covariance matrix of the estimates, available after calling fit().
        """

        def __init__(self):
                self.params = None
                self.cov_matrix = None
                self.observed_maturities = None
                self.observed_yields = None
                self.maturities = None
                self.predictions = None

        def _model(self, t, beta0 = 0.0, beta1 = 0.0, beta2 = 0.0, beta3 = 0.0, tau1 = 1.0, tau2 = 1.0):

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

        def fit(self, maturities, yields, p0=None):

                """
                Fits the NSS model's parameters to the observed data.
        
                Parameters
                ----------
                maturities : array_like
                        Observed maturities.
                yields : array_like
                        Observed yields.
                p0 : array_like, optional
                        Starting values for the 6 parameters [beta0, beta1, beta2, beta3,
                        tau1, tau2]. If not specified, a default estimation on observed data will be used.
                """

                self.observed_maturities = np.asarray(maturities, dtype=float)
                self.observed_yields = np.asarray(yields, dtype=float)
        
                bounds = (
                        [-np.inf, -np.inf, -np.inf, -np.inf, 1e-4, 1e-4],
                        [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
                )
        
                if p0 is None:
                        p0 = [yields[-1], yields[0] - yields[-1], 0.0, 0.0, 1.0, 5.0]
        
                self.params, self.cov_matrix = curve_fit(
                        self._model,
                        self.observed_maturities,
                        self.observed_yields,
                        p0=p0,
                        bounds=bounds,
                        maxfev=10000,
                )

                return self

        def predict(self, maturities):

                """
                Predicts yields for the specified maturities using the fitted NSS model.

                Parameters
                ----------
                maturities: array_like
                        Maturities for which to predict yields.

                Outputs
                -------
                predictions: np.ndarray
                        Predicted yields for the specified maturities.
                """

                if self.params is None:
                        raise RuntimeError("Model is not fitted yet. Call fit() first.")

                self.maturities = np.asarray(maturities, dtype=float)
                self.predictions = self._model(maturities, *self.params)

                return self.predictions

        def display(self):

                """
                Plot the calibrated NSS curve against the observed data.
                """

                if self.params is None:
                        raise RuntimeError("Model is not fitted yet. Call fit() first.")
                if self.predictions is None:
                        raise RuntimeError("No predictions available. Call predict() first.")


                fig, ax = plt.subplots()
                ax.plot(
                        self.maturities,
                        self.predictions,
                        label="Calibrated NSS Model",
                        color="blue",
                )

                ax.scatter(
                        self.observed_maturities,
                        self.observed_yields,
                        label="Observed Data",
                        color="red",
                )

                ax.legend()
                ax.set_title("NSS Curve Fit")
                ax.set_xlabel("Maturity")
                ax.set_ylabel("Yield")
                fig.tight_layout()
                plt.show()

        

if __name__ == "__main__":
        sample_maturities = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30]
        sample_yields = [ 0.03239, 0.02833, 0.02625, 0.02463, 0.02405, 0.02355, 0.02323, 0.02313, 0.02319, 0.02378, 0.02535, 0.02517, 0.02436, 0.02444]

        model = NSS()
        model.fit(sample_maturities, sample_yields)
        output_maturities = np.linspace(1, 30, 30)

        results = model.predict(output_maturities)

        model.display()
        print("Calibrated parameters [beta0, beta1, beta2, beta3, tau1, tau2]:")
        print(model.params)

        print("Predicted yields for maturities 1 to 30:")
        print(results)