from arc import Cesium as cs
import numpy as np
from scipy.interpolate import interp1d

class OpticalTransition:
    def __init__(self, laserWaist=25e-6, n1=6, l1=0, j1=0.5, mj1=0.5,
                 n2=7, l2=1, j2=1.5, mj2=1.5, q=0):
        """
        Initialize a transition between two energy levels in Cesium.
        
        Parameters
        ----------
        laserWaist : float, optional
            The waist of the laser in meters. Defaults to 25e-6.
        n1 : int, optional
            The principal quantum number of the lower energy level. Defaults to 6.
        l1 : int, optional
            The orbital angular momentum of the lower energy level. Defaults to 0.
        j1 : float, optional
            The total angular momentum of the lower energy level. Defaults to 0.5.
        mj1 : float, optional
            The magnetic quantum number of the lower energy level. Defaults to 0.5.
        n2 : int, optional
            The principal quantum number of the upper energy level. Defaults to 7.
        l2 : int, optional
            The orbital angular momentum of the upper energy level. Defaults to 1.
        j2 : float, optional
            The total angular momentum of the upper energy level. Defaults to 1.5.
        mj2 : float, optional
            The magnetic quantum number of the upper energy level. Defaults to 1.5.
        q : int, optional
            The polarization of the laser. Defaults to 0.
        
        Attributes
        ----------
        RabiAngularFreq_from_Power : callable
            A function that takes a power in W and returns the corresponding
            Rabi angular frequency.
        Power_from_RabiAngularFreq : callable
            A function that takes a Rabi angular frequency and returns
            the corresponding power in W.
        """
        self.laserWaist = laserWaist
        self.n1 = n1
        self.l1 = l1
        self.j1 = j1
        self.mj1 = mj1
        self.n2 = n2
        self.l2 = l2
        self.j2 = j2
        self.mj2 = mj2
        self.q = q
        
        self.RabiAngularFreq_from_Power = None
        self.Power_from_RabiAngularFreq = None
        
        #self.init_fast_lookup()
        
    def get_rabi_angular_freq(self, laserPower):
        """
        Compute the Rabi angular frequency for the transition.

        Parameters
        ----------
        laserPower : float
            The power of the laser, in W.

        Returns
        -------
        rabiFreq : float
            The Rabi angular frequency
        """
        if self.RabiAngularFreq_from_Power is None:
            rabiFreq = cs().getRabiFrequency(n1=self.n1, l1=self.l1,
                                               j1=self.j1,
                                               mj1=self.mj1,
                                               n2=self.n2,
                                               l2=self.l2,
                                               j2=self.j2, q=self.q,
                                               laserPower=laserPower,
                                               laserWaist=self.laserWaist)
        else:
            rabiFreq = self.RabiAngularFreq_from_Power(laserPower)

        return rabiFreq

# TODO: refactor this class to use two 2-level transitions for maximum code
#  reuse
class RydbergTransition:
    def __init__(self, laserWaist=25e-6, n1=6, l1=0, j1=0.5, mj1=0.5, q1=1,
                 n2=7, l2=1, j2=1.5, mj2=1.5, q2=1, n3=47, l3=2, j3=2.5):
        self.laserWaist = laserWaist
        self.n1 = n1
        self.l1 = l1
        self.j1 = j1
        self.mj1 = mj1
        self.n2 = n2
        self.l2 = l2
        self.j2 = j2
        self.mj2 = mj2
        self.n3 = n3
        self.l3 = l3
        self.j3 = j3
        self.q1 = q1
        self.q2 = q2
        self.RabiAngularFreq_1_from_Power = None
        self.RabiAngularFreq_2_from_Power = None
        self.Power_from_RabiAngularFreq_1 = None
        self.Power_from_RabiAngularFreq_2 = None

        self.init_fast_lookup()

    def init_fast_lookup(self):
        Pp = np.linspace(0, 100e-3, 100)
        Pp_RabiAngularFreq = []
        for p in Pp:
            Pp_RabiAngularFreq.append(self.get_e_rabi_angular_freq(laserPower=p))
        Pp_RabiAngularFreq = np.array(Pp_RabiAngularFreq)
        self.RabiAngularFreq_1_from_Power = interp1d(Pp, Pp_RabiAngularFreq,
                                                     kind='cubic')
        # inverse
        self.Power_from_RabiAngularFreq_1 = interp1d(Pp_RabiAngularFreq, Pp,
                                                     kind='cubic')

        Pc = np.linspace(0, 10, 100)
        Pc_RabiAngularFreq = []
        for p in Pc:
            Pc_RabiAngularFreq.append(self.get_r_rabi_angular_freq(laserPower=p))
        Pc_RabiAngularFreq = np.array(Pc_RabiAngularFreq)
        self.RabiAngularFreq_2_from_Power = interp1d(Pc, Pc_RabiAngularFreq,
                                                     kind='cubic')
        # inverse
        self.Power_from_RabiAngularFreq_2 = interp1d(Pc_RabiAngularFreq, Pc,
                                                     kind='cubic')

    def get_e_rabi_angular_freq(self, laserPower):
        """
        Compute the Rabi angular frequency for the excited state transition.

        Parameters
        ----------
        laserPower : float
            The power of the laser, in W.

        Returns
        -------
        rabiFreq_1 : float
            The Rabi angular frequency
        """
        if self.RabiAngularFreq_1_from_Power is None:
            rabiFreq_1 = cs().getRabiFrequency(n1=self.n1, l1=self.l1, j1=self.j1,
                                               mj1=self.mj1,
                                               n2=self.n2,
                                               l2=self.l2,
                                               j2=self.j2, q=self.q1,
                                               laserPower=laserPower,
                                               laserWaist=self.laserWaist)
        else:
            rabiFreq_1 = self.RabiAngularFreq_1_from_Power(laserPower)

        return rabiFreq_1

    def get_r_rabi_angular_freq(self, laserPower):
        """
        Compute the Rabi angular frequency for the Rydberg state transition.

        Parameters
        ----------
        laserPower : float
            The power of the laser, in W.

        Returns
        -------
        rabiFreq_2 : float
            The Rabi angular frequency
        """
        if self.RabiAngularFreq_2_from_Power is None:
            rabiFreq_2 = cs().getRabiFrequency(n1=self.n2, l1=self.l2, j1=self.j2, mj1=self.mj2, n2=self.n3,
                                               l2=self.l3,
                                               j2=self.j3, q=self.q2,
                                               laserPower=laserPower,
                                               laserWaist=self.laserWaist)
        else:
            rabiFreq_2 = self.RabiAngularFreq_2_from_Power(laserPower)

        return rabiFreq_2
    
    def get_balanced_laser_power(self, probe_power=None, couple_power=None):
        """
        Compute the balanced laser power for the probe and couple lasers. This is
        the laser power that results in the same Rabi frequency for both lasers.
    
        Parameters
        ----------
        probe_power : float, optional
            The power of the probe laser, in W.
        couple_power : float, optional
            The power of the couple laser, in W.
    
        Returns
        -------
        probe_power : float, optional
            The power of the probe laser, in W.
        couple_power : float, optional
            The power of the couple laser, in W.
        """
        if probe_power is None:
            couple_rabi = self.RabiAngularFreq_2_from_Power(couple_power)
            probe_power = self.Power_from_RabiAngularFreq_1(couple_rabi)
            return probe_power # in W
        elif couple_power is None:
            probe_rabi = self.RabiAngularFreq_1_from_Power(probe_power)
            couple_power = self.Power_from_RabiAngularFreq_2(probe_rabi)
            return couple_power # in W
        else:
            print("You messed up")
            pass

    def get_e_linewidth(self):
        """
        This function computes the linewidth of the excited state, given by the
        inverse of the lifetime of the state.
    
        Returns
        -------
        gamma2 : float
            The linewidth of the excited state, in Hz.
        """
        gamma2 = 1 / cs().getStateLifetime(self.n2, self.l2, self.j2,
                                           temperature=300.0,
                                           includeLevelsUpTo=self.n2 + 5)
        return gamma2  # in Hz

    def get_r_linewidth(self):
        """
        This function computes the linewidth of the Rydberg state, given by the
        inverse of the lifetime of the state.

        Returns
        -------
        gamma3 : float
            The linewidth of the Rydberg state, in Hz.
        """
        gamma3 = 1 / cs().getStateLifetime(self.n3, self.l3, self.j3,
                                           temperature=300.0,
                                           includeLevelsUpTo=self.n3 + 5)
        return gamma3  # in Hz

    def get_e_transition_freq(self):
        """
        Compute the transition frequency for the excitation laser, taking into
        account the hyperfine structure of the ground and excited states.
        Returned values is given relative to the centre of gravity of the
        hyperfine-split states.

        Returns
        -------
        float
            The transition frequency, in Hz.
        """
        freq_1 = cs().getTransitionFrequency(n1=self.n1, l1=self.l1, j1=self.j1,
                                             n2=self.n2, l2=self.l2,
                                             j2=self.j2)
        HFS_g = cs().getHFSEnergyShift(j=self.j1, f=4,
                                       A=cs().getHFSCoefficients(n=self.n1,
                                                                 l=self.l1,
                                                                 j=self.j1)[0])
        HFS_e = cs().getHFSEnergyShift(j=self.j2, f=5,
                                       A=cs().getHFSCoefficients(n=self.n2,
                                                                 l=self.l2,
                                                                 j=self.j2)[0])
        return freq_1 - HFS_g + HFS_e  # in Hz

    def get_r_transition_freq(self):
        """
        Compute the transition frequency for the Rydberg laser, taking into
        account the hyperfine structure of the ground and excited states.
        Returned values is given relative to the centre of gravity of the
        hyperfine-split states.

        Returns
        -------
        float
            The transition frequency, in Hz.
        """
        freq_2 = cs().getTransitionFrequency(n1=self.n2, l1=self.l2, j1=self.j2, n2=self.n3, l2=self.l3,
                                             j2=self.j3)
        HFS_e = cs().getHFSEnergyShift(j=self.j2, f=5,
                                       A=cs().getHFSCoefficients(n=self.n2,
                                                                 l=self.l2, j=self.j2)[0])
        # ARC doesn't calculate hyperfine structure for n=47, l=2, j=2.5?
        return freq_2 - HFS_e  # in Hz

    def get_e_saturation_power(self):
        """
        Compute the saturation power for the E transition.
    
        The saturation power is given by the intensity required to saturate the
        transition, multiplied by the area of the beam.
    
        Returns
        -------
        float
            The saturation power of the excitation laser, in W.
        """
        sat_1 = cs().getSaturationIntensityIsotropic(ng=self.n1, lg=self.l1, jg=self.j1, fg=4,
                                                     ne=self.n2, le=self.l2,
                                                     je=self.j2, fe=5)
        return sat_1 * np.pi * self.laserWaist**2  # in Watts

    def get_r_saturation_power(self):
        """
        Compute the saturation power for the E transition.

        The saturation power is given by the intensity required to saturate the
        transition, multiplied by the area of the beam.

        Returns
        -------
        float
            The saturation power of the excitation laser, in W.
        """
        sat_2 = cs().getSaturationIntensityIsotropic(ng=self.n2, lg=self.l2, jg=self.j2, fg=5,
                                                     ne=self.n3, le=self.l3,
                                                     je=self.j3, fe=6)
        return sat_2 * np.pi * self.laserWaist**2  # in Watts

    def get_optimal_detuning(self, P1=None, P2=None, rabiFreq1=None,
                             rabiFreq2=None, gamma2=None, gamma3=None):
        """
        Calculate the optimal detuning of the Rydberg laser, given the powers of
        the two lasers or their Rabi frequencies.

        Parameters
        ----------
        P1 : float, optional
            The power of the probe laser, in W.
        P2 : float, optional
            The power of the couple laser, in W.
        rabiFreq1 : float, optional
            The Rabi frequency of the probe laser, in Hz.
        rabiFreq2 : float, optional
            The Rabi frequency of the couple laser, in Hz.
        gamma2 : float, optional
            The linewidth of the intermediate state, in Hz.
        gamma3 : float, optional
            The linewidth of the Rydberg state, in Hz.

        Returns
        -------
        float
            The optimal detuning of the Rydberg laser, in Hz.

        Notes
        -----
        The optimal detuning is calculated following the procedure outlined in
        the Rydberg parameters notebook.
        """
        if gamma2 is None or gamma3 is None:
            gamma2 = self.get_e_linewidth()
            gamma3 = self.get_r_linewidth()

        if rabiFreq1 is not None and rabiFreq2 is not None:
            Delta = np.sqrt(rabiFreq1**2 + rabiFreq2**2) / 2 * np.sqrt(gamma2 / (2 * gamma3))
            return Delta
        elif P1 is not None and P2 is not None:
            rabiFreq1 = self.get_e_rabi_angular_freq(laserPower=P1)
            rabiFreq2 = self.get_r_rabi_angular_freq(laserPower=P2)
            Delta = np.sqrt(rabiFreq1**2 + rabiFreq2**2) / 2 * np.sqrt(gamma2 / (2 * gamma3))
            return Delta
        else:
            raise ValueError("Must specify either P1, P2 or rabiFreq1, rabiFreq2")

    def get_total_rabi_angular_freq(self, Pp, Pc, resonance=False):
        """
        Compute the total Rabi angular frequency of the two-photon transition.

        Parameters
        ----------
        Pp : float
            The power of the probe laser, in W.
        Pc : float
            The power of the couple laser, in W.
        resonance : bool, optional
            If True, the resonance condition is assumed to be satisfied.
            If False (default), the optimal detuning is calculated.

        Returns
        -------
        float
            The total Rabi angular frequency of the two-photon transition, in
            Hz.

        Notes
        -----
        The total Rabi angular frequency is calculated as the geometric mean of
        the Rabi angular frequencies of the two lasers, divided by the
        optimal detuning.
        If the resonance condition is assumed to be satisfied, the detuning is
        neglected.
        """
        rabiFreq_1 = self.get_e_rabi_angular_freq(laserPower=Pp)
        rabiFreq_2 = self.get_r_rabi_angular_freq(laserPower=Pc)
        if not resonance:
            Delta0 = self.get_optimal_detuning(rabiFreq1=rabiFreq_1,
                                               rabiFreq2=rabiFreq_2)
            return rabiFreq_1 * rabiFreq_2 / 2 / Delta0
        else:
            return 0.5 * np.sqrt(rabiFreq_1**2 + rabiFreq_2**2)

    def get_pi_pulse_duration(self, Pp, Pc, resonance=False):
        """
        Compute the duration of a pi pulse of the two-photon transition.

        Parameters
        ----------
        Pp : float
            The power of the probe laser, in W.
        Pc : float
            The power of the couple laser, in W.
        resonance : bool, optional
            If True, the resonance condition is assumed to be satisfied.
            If False (default), the optimal detuning is calculated.

        Returns
        -------
        float
            The duration of a pi pulse of the two-photon transition, in seconds.

        Notes
        -----
        The duration of a pi pulse is calculated as pi / total Rabi angular
        frequency, where the total Rabi angular frequency is calculated as the
        geometric mean of the Rabi angular frequencies of the two lasers,
        divided by the optimal detuning.
        If the resonance condition is assumed to be satisfied, the detuning is
        neglected.
        """
        omega = self.get_total_rabi_angular_freq(Pp, Pc, resonance=resonance)
        return np.pi / omega
    
    def get_pi_detuning(self, probe_power, couple_power, pi_time):
        """
        Calculate the detuning required to implement a pi pulse of specified
        duration.
        
        Parameters
        ----------
        probe_power : float
            The power of the probe laser, in W.
        couple_power : float
            The power of the coupling laser, in W.
        pi_time : float
            The desired duration of the pi pulse, in seconds.
        
        Returns
        -------
        float
            The detuning required to achieve the specified pi pulse duration.
        """
        rabiFreq_1 = self.get_e_rabi_angular_freq(laserPower=probe_power)
        rabiFreq_2 = self.get_r_rabi_angular_freq(laserPower=couple_power)
        detuning = pi_time/np.pi/2 * rabiFreq_1 * rabiFreq_2
        
        return detuning

    def print_laser_frequencies(self, Pp, Pc, AOM456=-220e6, AOM1064=-110e6):
        trans1 = self.get_e_transition_freq()
        line1 = self.get_e_linewidth()
        trans2 = self.get_r_transition_freq()
        line2 = self.get_r_linewidth()
        rabiFreq_1 = self.get_e_rabi_angular_freq(laserPower=Pp)
        rabiFreq_2 = self.get_r_rabi_angular_freq(laserPower=Pc)
        Delta0 = self.get_optimal_detuning(rabiFreq1=rabiFreq_1, rabiFreq2=rabiFreq_2)

        print(trans1)
        print("Probe laser frequency (with AOM)", (trans1 - AOM456) * 1e-9,
              "GHz")
        print(r"Power Broadening $\sqrt(2)*\Omega = $", np.sqrt(2) *
              rabiFreq_1 / (2*np.pi) * 1e-6, "MHz")
        print("Natural Linewidth", line1 * 1e-6, "MHz")
        print("Couple laser frequency (with AOM)", (trans2 - AOM1064) * 1e-9,
                                                    "GHz")
        print(r"Power Broadening $\sqrt(2)*\Omega = $", np.sqrt(2) *
              rabiFreq_2 / (2*np.pi) * 1e-6, "MHz")
        print("Natural Linewidth", line2 * 1e-6, "MHz")

        print("\nOptimal detuning", Delta0 * 1e-9 / (2 * np.pi), "GHz ")

        print("\nOptimal probe frequency (with AOM)", (trans1 + Delta0 / (2 *
                                                                     np.pi) -
                                            AOM456) * 1e-9, "GHz")
        print("Optimal couple frequency (with AOM)", (trans2 - Delta0 / (2 *
                                                                     np.pi) -
                                           AOM1064) * 1e-9, "GHz")

        print("\nExpected Rabi Frequency = 2*pi",
              self.get_total_rabi_angular_freq(Pp, Pc) * 1e-6 / (2 * np.pi), "MHz")
        print("Pi Pulse Duration", self.get_pi_pulse_duration(Pp, Pc) * 1e9, "ns")

    def print_tweezer_stark_shift(self, tweezer_power):
        # TODO: update this function to use the calculators from ac_stark.py
        # Two state approximation here is not very accurate
        rabiFreq_2 = cs().getRabiFrequency(n1=self.n2, l1=self.l2, j1=self.j2,
                                           mj1=self.mj2, n2=self.n3,
                                           l2=self.l3,
                                           j2=self.j3, q=self.q2,
                                           laserPower=tweezer_power,
                                           laserWaist=1e-6)

        transition_frequency = self.get_r_transition_freq()
        print("Transition Frequency (GHz)", transition_frequency * 1e-9)
        tweezer_frequency = 2.99792e8 / (1069.79e-9)
        print("Tweezer Frequency (GHz)", tweezer_frequency * 1e-9)
        tweezer_detuning = transition_frequency - tweezer_frequency
        print("Tweezer Detuning (GHz)", tweezer_detuning * 1e-9)
        stark_shift = rabiFreq_2**2 / 4 / (2 * np.pi * tweezer_detuning)
        print("Tweezer Stark Shift (MHz)", stark_shift / (2 * np.pi) * 1e-6)

    def print_ac_stark_shift(self, Pp, Pc):
        # TODO: update this function to use the calculators from ac_stark.py
        diff_Stark = self.get_diff_ryd_ac_stark(Pp, Pc)
        print("Differential Stark Shift (MHz)", diff_Stark / (2 * np.pi) * 1e-6)

        rabiFreq_1 = self.get_e_rabi_angular_freq(laserPower=Pp)
        rabiFreq_2 = self.get_r_rabi_angular_freq(laserPower=Pc)
        Delta0 = self.get_optimal_detuning(rabiFreq1=rabiFreq_1, rabiFreq2=rabiFreq_2)

        Stark_1 = rabiFreq_1**2 / 4 / Delta0
        Stark_2 = rabiFreq_2**2 / 4 / Delta0
        print("Stark Shift 1 (MHz)", Stark_1 / (2 * np.pi) * 1e-6)
        print("Stark Shift 2 (MHz)", Stark_2 / (2 * np.pi) * 1e-6)
        
    def print_saturation_powers(self):
        # get the saturation powers for the probe and coupling transitions
        satPower_E = self.get_e_saturation_power()
        satPower_R = self.get_r_saturation_power()
        
        print("Saturation Power E (mW)", satPower_E * 1e3)
        print("Saturation Power R (mW)", satPower_R * 1e3)


if __name__ == '__main__':
    transition40 = RydbergTransition(laserWaist=25e-6, n1=6, l1=0, j1=0.5,
                                     mj1=0.5, n2=7, l2=1, j2=1.5, mj2=1.5,
                                     q2=-1, n3=40, l3=0, j3=0.5)

    transition40.print_laser_frequencies(Pp=0.010, Pc=2)
    transition40.print_tweezer_stark_shift(tweezer_power=0.010)
    transition40.print_ac_stark_shift(Pp=0.010, Pc=2)
