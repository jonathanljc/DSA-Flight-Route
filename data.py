# DOWNLOAD GEOPY to calculate distance between Latitude and longitude
# do: pip install geopy
from geopy.distance import geodesic as GD

def filterData():
    data=open("airports.dat", "r", encoding='utf8')
    totalAirport = []
    for line in data:
        eachAirport = []
        split = line.split(',')
        if "Asia" in split[11]:
            eachAirport.append(split[1].strip('"'))     # Airport Name
            eachAirport.append(split[2].strip('"'))     # City
            eachAirport.append(split[3].strip('"'))     # Country
            eachAirport.append(split[4].strip('"'))     # IATA code
            eachAirport.append(float(split[6]))         # Latitude
            eachAirport.append(float(split[7]))         # Longitude
            totalAirport.append(eachAirport)
    return totalAirport

def calculateDistance(latitude1, longitude1, latitude2, longitude2):
    location1 = (latitude1, longitude1)
    location2 = (latitude2, longitude2)

    distance = GD(location1, location2).km
    print(str(distance) + " kilometers")    # check result
    return distance

airportData = filterData()
print(str(len(airportData)) + " airports in Asia")
print(airportData[55])        # Just to check and see at index

# test calculate distance between airport 500 and airport 600
calculateDistance(airportData[500][4], airportData[500][5], airportData[600][4], airportData[600][5])
