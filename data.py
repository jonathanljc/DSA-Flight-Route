# Import geodesic function from geopy.distance to calculate geographical distance
from geopy.distance import geodesic as GD

# Function to filter data from the airports.dat file
def filterData():
    # Open the file in read mode with utf8 encoding
    data=open("airports.dat", "r", encoding='utf8')
    totalAirport = []  # Initialize an empty list to store airport data

    # Loop through each line in the file
    for line in data:
        eachAirport = []  # Initialize an empty list to store individual airport data
        split = line.split(',')  # Split the line by comma

        # If the line contains "Asia", add relevant data to the eachAirport list
        if "Asia" in split[11]:
            eachAirport.append(split[1].strip('"'))     # Airport Name
            eachAirport.append(split[2].strip('"'))     # City
            eachAirport.append(split[3].strip('"'))     # Country
            eachAirport.append(split[4].strip('"'))     # IATA code
            eachAirport.append(float(split[6]))         # Latitude
            eachAirport.append(float(split[7]))         # Longitude

            # Add the eachAirport list to the totalAirport list
            totalAirport.append(eachAirport)

    # Return the totalAirport list
    return totalAirport

# Function to calculate distance between two geographical locations
def calculateDistance(latitude1, longitude1, latitude2, longitude2):
    location1 = (latitude1, longitude1)  # Create a tuple for location 1
    location2 = (latitude2, longitude2)  # Create a tuple for location 2

    # Calculate the distance between the two locations in kilometers
    distance = GD(location1, location2).km

    # Print the distance for checking
    print(str(distance) + " kilometers")

    # Return the distance
    return distance

# Call the filterData function and store the result in airportData
airportData = filterData()

# Print the number of airports in Asia
print(str(len(airportData)) + " airports in Asia")

# Print the data for the airport at index 55 for checking
print(airportData[55])

# Test the calculateDistance function by calculating the distance between airport 500 and airport 600
calculateDistance(airportData[500][4], airportData[500][5], airportData[600][4], airportData[600][5])