# Import geodesic function from geopy.distance to calculate geographical distance
# Install the geopy package if not already installed
# pip3 install geopy (mac), pip install geopy (windows) 

from geopy.distance import geodesic as GD

# Function to filter data from the airports.dat file
# totalAirpot is a dictionary that contains a dictionary of all airports in Asia
# totalAirport uses the IATA code as the key and the value is a dictionary containing the name, city, country, IATA code, latitude and longitude of the airport

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

# Function to filter route data from routes.dat file using the airport data from the filterAirportData function
# routes is a list of dictionaries containing the source, destination and airline ID of each route
# The source and destination are the IATA codes of the airports

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

# Function to filter airline data from airlines.dat file with airline ID and airline name
# airlines is a list of dictionaries containing the airline ID and airline name of each airline
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