import libs.ComsChannelsSim.PowerElement as PowerElement
import libs.ComsChannelsSim.ChannelElement as ChannelElement
import libs.ComsChannelsSim.utils as rf_utils

import matplotlib.pyplot as plt

class Transceiver:
    def __init__(self, tx_power, sensibility_dB, frequency):

        # b
        amp1 = PowerElement.powerElement(gain_dB = 10, figure = 3)
        amp2 = PowerElement.powerElement(gain_dB = 10, figure = 3, previousElement = amp1)
        cable1 = PowerElement.powerElement(attenuation_dB = 10, previousElement = amp2)
        cable2 = PowerElement.powerElement(attenuation_dB = 10, previousElement = cable1)

        print("Exercise:")
        cable2.printEquivalentValues()

        # Define the antenna and circulator to be used
        antenna = PowerElement.powerElement(gain_dB = 5)
        circulator = PowerElement.powerElement(attenuation_dB = 0.3, previousElement = antenna)

        # Define characteristics of the transmitter
        amp = PowerElement.powerElement(gain_dB = 20, figure = 6.3, previousElement = circulator)
        self.transmitter = PowerElement.powerElement(gain = 2, figure = 2, previousElement = amp)

        # Define the characteristics of the receiver
        lna = PowerElement.powerElement(gain_dB = 30, figure = 1.7, previousElement = circulator)
        self.receiver = PowerElement.powerElement(gain_dB = 12, figure = 2.95, previousElement = lna)

        # Store the relevant information
        self.tx_power_dB = rf_utils.NaturalToLogarithmic(tx_power)
        self.sensibility_dB = sensibility_dB
        self.frequency = frequency
    
    def get_PIRE(self):
        return self.tx_power_dB + self.transmitter.calculateEquivalentGain()

    def get_sensibility(self):
        return self.sensibility_dB - self.receiver.calculateEquivalentGain()

class Vanet:
    def __init__(self, vehicles_transceiver_properties):
        
        # Defining the type of channel used for transmissions
        self.channel = ChannelElement.channelElement("AWGN")

        # Defining all vehicle transceivers
        self.vehicle_transceivers = []
        for vehicle_transceiver_properties in vehicles_transceiver_properties:
        
            # Defining the typical transceiver on any vehicle
            self.vehicle_transceivers.append(Transceiver(vehicle_transceiver_properties.get("tx_power", 0), vehicle_transceiver_properties.get("sensibility", 0), vehicle_transceiver_properties.get("frequency", 0)))
    
    def calculate_max_distances(self):

        # Distances
        max_distances = []

        # Calculate the distance
        for vehicle_transceiver in self.vehicle_transceivers:

            # Calculating the distance with the hata Suburban model
            distance = self.channel.calculateDistance_sensitivity(transmittedPower_dB = vehicle_transceiver.get_PIRE(),
                                                                       sensitivity_dB = vehicle_transceiver.get_sensibility(),
                                                                       standardDeviation_dB = 3,
                                                                       lossModel = "hataSuburban",
                                                                       baseHeight = 2,
                                                                       mobileHeight = 3,
                                                                       frequency = vehicle_transceiver.frequency)
            
            # Add the distance
            max_distances.append(distance)
        
        return max_distances
    
    def plot_distance_power(self):

        for vehicle_transceiver in self.vehicle_transceivers:
            self.channel.plotDistance_ReceivedPower(transmittedPower_dB = vehicle_transceiver.get_PIRE(),
                                                                       sensitivity_dB = vehicle_transceiver.get_sensibility(),
                                                                       standardDeviation_dB = 3,
                                                                       lossModel = "hataSuburban",
                                                                       baseHeight = 2,
                                                                       mobileHeight = 3,
                                                                       frequency = vehicle_transceiver.frequency,
                                                                       minDistance = 1,
                                                                       maxDistance = 200)
        
        plt.show()