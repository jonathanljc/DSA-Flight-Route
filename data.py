# Import geodesic function from geopy.distance to calculate geographical distance
# Install the geopy package if not already installed
# pip3 install geopy (mac), pip install geopy (windows) 

from geopy.distance import geodesic as GD

# Function to filter data from the airports.dat file
# totalAirpot is a dictionary that contains a dictionary of all airports in Asia
# totalAirport uses the IATA code as the key and the value is a dictionary containing the name, city, country, IATA code, latitude and longitude of the airport
class DataFilter:
    def __init__(self):
        self.airport_data = self.filter_airport_data()
        self.route_data = self.filter_route_data()
        self.airport_data = self.filter_airport_data_further()
        self.airline_data = self.filter_airline()

    def filter_airport_data(self):
        with open("airports.dat", "r", encoding='utf8') as data:
            total_airport = {}

            for line in data:
                split = line.split(',')

                if "Asia" in split[11]:
                    each_airport = {
                        "name": split[1].strip('"'),
                        "city": split[2].strip('"'),
                        "country": split[3].strip('"'),
                        "iata": split[4].strip('"'),
                        "latitude": float(split[6]),
                        "longitude": float(split[7])
                    }

                    total_airport[each_airport["iata"]] = each_airport

        return total_airport

    def filter_airport_data_further(self):
        new_airport_data = {}
        for airport in self.airport_data:
            for route in self.route_data:
                if (airport == route["source"]) or (airport == route["destination"]):
                    new_airport_data[airport] = self.airport_data[airport]
                    break

        return new_airport_data

    def filter_route_data(self):
        with open("routes.dat", "r", encoding='utf8') as data:
            routes = []

            for line in data:
                split = line.split(',')

                if split[2].strip('"') in self.airport_data:
                    each_route = {
                        "source": split[2].strip('"'),
                        "destination": split[4].strip('"'),
                        "airlineID": split[1].strip('"')
                    }

                    routes.append(each_route)

        return routes

    def calculate_distance(self, latitude1, longitude1, latitude2, longitude2):
        location1 = (latitude1, longitude1)
        location2 = (latitude2, longitude2)
        distance = GD(location1, location2).km
        return distance

    def filter_airline(self):
        with open("airlines.dat", "r", encoding='utf8') as data:
            airlines = []

            for line in data:
                split = line.split(',')

                each_airline = {
                    "airlineID": split[0].strip('"'),
                    "airlineName": split[1].strip('"'),
                }

                airlines.append(each_airline)

        return airlines