import csv
from dataclasses import dataclass


def readFile(filename: str):
    with open(filename, mode='r') as file:
        data = csv.reader(file)

        # titles = data.__next__()
        for line in data:
            print(line)


readFile("UAM Test Data.csv")


class Level0HardwareGivens:
    vehicle_range: float
    max_speed: float
    energy_cap: float
    energy_consumption_dist: float
    num_passengers: float
    max_luggage_weight: float
    vehicle_base_cost: float
    ingress_egress_time: float
    landing_takeoff_time: float
    bad_event_probability: float
    vehicle_base_weight: float
    max_total_passenger_weight: float

    def __init__(self, vehicle_range: float, max_speed: float, energy_cap: float, energy_consumption_dist: float,
                 num_passengers: float, max_luggage_weight: float, vehicle_base_cost: float, ingress_egress_time: float,
                 landing_takeoff_time: float, bad_event_probability: float, vehicle_base_weight: float,
                 max_total_passenger_weight: float):
        self.vehicle_range = vehicle_range
        self.max_speed = max_speed
        self.energy_cap = energy_cap
        self.energy_consumption_dist = energy_consumption_dist
        self.num_passengers = num_passengers
        self.max_luggage_weight = max_luggage_weight
        self.vehicle_base_cost = vehicle_base_cost
        self.ingress_egress_time = ingress_egress_time
        self.landing_takeoff_time = landing_takeoff_time
        self.bad_event_probability = bad_event_probability
        self.vehicle_base_weight = vehicle_base_weight
        self.max_total_passenger_weight = max_total_passenger_weight


class Level0GeographicGivens:
    energy_cost: float
    airspace_classification: str
    max_charging_refuel_rate: float
    trip_dist: float
    land_cost: float
    building_cost: float
    av_taxi_cost: float
    av_rideshare_cost: float
    median_household_income: float
    living_cost: float
    num_emergency_landing_sites: float

    def __init__(self, energy_cost: float, airspace_classification: str, max_charging_refuel_rate: float,
                 trip_dist: float, land_cost: float, building_cost: float, av_taxi_cost: float,
                 av_rideshare_cost: float, median_household_income: float, living_cost: float,
                 num_emergency_landing_sites: float):
        self.energy_cost = energy_cost
        self.airspace_classification = airspace_classification
        self.max_charging_refuel_rate = max_charging_refuel_rate
        self.trip_dist = trip_dist
        self.land_cost = land_cost
        self.building_cost = building_cost
        self.av_taxi_cost = av_taxi_cost
        self.av_rideshare_cost = av_rideshare_cost
        self.median_household_income = median_household_income
        self.living_cost = living_cost
        self.num_emergency_landing_sites = num_emergency_landing_sites


class Level0UserGivens:
    total_trip_time: float
    max_tolerable_trip_cost: float
    max_tolerable_ingress_egress_time: float
    max_possible_luggage_per_passenger_weight: float
    num_trip_passengers: float

    def __init__(self, total_trip_time: float, max_tolerable_trip_cost: float, max_tolerable_ingress_egress_time: float,
                 max_possible_luggage_per_passenger_weight: float, num_trip_passengers: float):
        self.total_trip_time = total_trip_time
        self.max_tolerable_trip_cost = max_tolerable_trip_cost
        self.max_tolerable_ingress_egress_time = max_tolerable_ingress_egress_time
        self.max_possible_luggage_per_passenger_weight = max_possible_luggage_per_passenger_weight
        self.num_trip_passengers = num_trip_passengers


class Level0EconomicGivens:
    corp_overhead_costs: float
    general_target_price_per_passenger_ride: float
    flight_controller_employment_cost: float
    break_even_point: float

    def __init__(self, corp_overhead_costs: float, general_target_price_per_passenger_ride: float,
                 flight_controller_employment_cost: float, break_even_point: float):
        self.corp_overhead_costs = corp_overhead_costs
        self.general_target_price_per_passenger_ride = general_target_price_per_passenger_ride
        self.flight_controller_employment_cost = flight_controller_employment_cost
        self.break_even_point = break_even_point


@dataclass
class Level0:
    hardware: Level0HardwareGivens
    geography: Level0GeographicGivens
    user: Level0UserGivens
    economy: Level0EconomicGivens

    def __init__(self, hardware: Level0HardwareGivens, geography: Level0GeographicGivens, user: Level0UserGivens,
                 economy: Level0EconomicGivens):
        self.hardware = hardware
        self.geography = geography
        self.user = user
        self.economy = economy


class Level1:
    level0: Level0
    total_energy_cost_per_trip: float
    trip_possible: bool
    total_charge_time: float
    desirable_time: bool
    desirable_luggage: bool

    def __init__(self, level0: Level0):
        self.level0 = level0
        self.total_energy_cost_per_trip = (level0.hardware.energy_cap - (level0.hardware.energy_cap - (
                level0.hardware.energy_consumption_dist * level0.geography.trip_dist))) * \
                                          level0.geography.energy_cost

        self.trip_possible = level0.hardware.range > level0.geography.trip_dist
        self.total_charge_time = (level0.hardware.energy_cap - (level0.hardware.energy_cap - (
                level0.hardware.energy_consumption_dist * level0.geography.trip_dist))) / \
                                 level0.geography.max_charging_refuel_rate

        self.desirable_time = level0.hardware.max_speed >= level0.geography.trip_dist / level0.user.total_trip_time
        luggage_per_person = (level0.hardware.max_luggage_weight / level0.hardware.num_passengers)
        self.desirable_luggage = luggage_per_person >= level0.user.max_possible_luggage_per_passenger_weight


class Level2:
    level0: Level0
    level1: Level1
    energy_cost_by_weight_at_max_weight: float
    desirable_ingress_egress_time: bool

    def __init__(self, level1: Level1):
        self.level1 = level1
        self.level0 = level1.level0
        total_weight = self.level0.hardware.vehicle_base_weight + self.level0.hardware.max_total_passenger_weight
        total_weight += self.level0.hardware.max_luggage_weight
        self.energy_cost_by_weight_at_max_weight = level1.total_energy_cost_per_trip / total_weight

        egress_ratio = self.level0.user.max_tolerable_ingress_egress_time / self.level0.hardware.ingress_egress_time
        self.desirable_ingress_egress_time = level1.total_charge_time <= egress_ratio
