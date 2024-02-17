# Import geodesic function from geopy.distance to calculate geographical distance
from geopy.distance import geodesic as GD

# Function to filter data from the airports.dat file
def filterData():
    with open("airports.dat", "r", encoding='utf8') as data:
        totalAirport = {}

        for line in data:
            split = line.split(',')

            if "Asia" in split[11]:
                eachAirport = {
                    "name": split[1].strip('"'),
                    "city": split[2].strip('"'),
                    "country": split[3].strip('"'),
                    "iata": split[4].strip('"'),
                    "latitude": float(split[6]),
                    "longitude": float(split[7])
                }

                totalAirport[eachAirport["iata"]] = eachAirport

    return totalAirport

# Function to calculate distance between two geographical locations
def calculateDistance(latitude1, longitude1, latitude2, longitude2):
    location1 = (latitude1, longitude1)  # Create a tuple for location 1
    location2 = (latitude2, longitude2)  # Create a tuple for location 2

    # Calculate the distance between the two locations in kilometers
    distance = GD(location1, location2).km

    # Print the distance for checking
    # print(str(distance) + " kilometers")

    # Return the distance
    return distance

