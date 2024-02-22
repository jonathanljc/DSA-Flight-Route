# Import geodesic function from geopy.distance to calculate geographical distance
from geopy.distance import geodesic as GD

# Function to filter data from the airports.dat file
def filterAirportData():
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

def filterAirportDataFurther(airportData, routeData):
    newAirportData = {}
    for airport in airportData:
        for route in routeData:
            if (airport == route["source"]) or (airport == route["destination"]):
                newAirportData[airport] = airportData[airport]
                break
    
    return newAirportData

# Function to filter route data from routes.dat file
def filterRouteData(airportData):
    with open("routes.dat", "r", encoding='utf8') as data:
        routes = []

        for line in data:
            split = line.split(',')

            if split[2].strip('"') in airportData:
                # print(split[2].strip('"'))
                eachRoute = {
                    "source": split[2].strip('"'),
                    "destination": split[4].strip('"'),
                    "airlineID": split[1].strip('"')
                }

                routes.append(eachRoute)

    # print(routes)
    return routes

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

def filterAirline():
    with open("airlines.dat", "r", encoding='utf8') as data:
        airlines = []

        for line in data:
            split = line.split(',')

            eachAirline = {
                "airlineID": split[0].strip('"'),
                "airlineName": split[1].strip('"'),
            }
            
            airlines.append(eachAirline)

    # print(airlines)
    return airlines