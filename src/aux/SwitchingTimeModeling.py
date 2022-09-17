import math


class SwitchingTimeModeling:

    def __init__(self, d1=16, t_sw1=10*math.pow(10, -9), d2=1024, t_sw2=500*math.pow(10, -9)):
        self.d1 = d1
        self.t_sw1 = t_sw1  # Switching times in s
        self.d2 = d2
        self.t_sw2 = t_sw2  # Switching times in s

    def get_V_d(self, dimension):
        on = True

        # From "RxNN: A Framework for Evaluating Deep Neural Networks on Resistive Crossbars"
        r_wire = 3.3 * math.pow(10, 6)  # Unit resistance of a wire in Ω/m

        # From "CCCS: customized spice-level crossbar-array circuit simulator for in-memory computing"
        # Wire resistance between adjacent cells R_wire = 2.82 Ω
        # R_wire = r_wire * l_wire
        # => l_wire = R_wire / r_wire
        R_wire = 2.82
        l_wire = R_wire / r_wire  # Wire length in m

        # From "Cross-Point memory Array Without Cell Selectors - Device Characteristics and Data Storage Pattern Dependencies"
        R_on = 5 * math.pow(10, 3)  # Low resistance state in Ω
        R_off = math.pow(10, 6)  # High resistance state in Ω
        if on:
            R_device = R_on
        else:
            R_device = R_off

        # From "Overcoming the Challenges of Crossbar Resistive Memory Architectures"
        V_write = 3.2  # Write voltage in V

        rows = dimension
        columns = dimension

        V_d = V_write * R_device / ((rows + columns) * r_wire * l_wire + R_device)

        return V_d

    def get_constants(self):
        V_d1 = self.get_V_d(self.d1)
        V_d2 = self.get_V_d(self.d2)

        k1 = math.log(self.t_sw2 / self.t_sw1) / (V_d1 - V_d2)
        k2 = self.t_sw1 * math.pow(math.e, k1 * V_d1)
        return k1, k2
