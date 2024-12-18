# ✈️ Flight Map Routing System (CSC1108-DATA STRUCTURES AND ALGORITHMS)

Welcome to the **Flight Map Routing System**! This project combines real-world datasets, advanced algorithms, and an intuitive graphical user interface to solve routing problems efficiently.

## 📜 Project Description

The **Flight Map Routing System** is a Python-based application designed to:
- 🚀 Find the **shortest path** between airports.
- 🛫 Offer multiple criteria for ranking routes:
  - Shortest Distance
  - Fewest Connections
  - Most Cost-Effective
- 🌍 Visualize flight routes on a map with clear and interactive UI components.

This project leverages advanced data structures (e.g., graphs, KD-Trees) and algorithms (e.g., Dijkstra, A*, Bellman-Ford, DFS) to optimize routing efficiency.

---

## ✨ Features

1. **🗺️ Dataset Integration**:
   - Filters airports and routes to include only commercial flights within Asia.
   - Uses the OpenFlights dataset with enhanced attributes like distances and costs.

2. **🔗 Graph Representation**:
   - Airports and routes are modeled using **adjacency lists**.
   - KD-Trees improve search efficiency for multi-dimensional data (latitude, longitude).

3. **📈 Pathfinding Algorithms**:
   - **Dijkstra's Algorithm**: Finds the shortest path for non-negative weights.
   - **A'*' Algorithm**: Uses heuristics for faster searches.
   - **Bellman-Ford Algorithm**: Handles graphs with negative weights.
   - **DFS Algorithm**: Systematically explores all possible paths.



4. **🎨 Graphical User Interface (GUI)**:

   <img src="https://github.com/jonathanlimjingchuan/CSC1108-DSA-FlightRoute/raw/main/GUI.png" alt="GUI Example" width="500"/>

   - Built with **CustomTkinter** and **TkinterMapView**.
   - Interactive map displays flight routes, airports, and search results.
   - Users input source and destination airport codes to view results instantly.



6. **📊 Data Visualization**:
   - Displays flight paths based on various algorithms.
   - Highlights the cheapest/fastest routes and allows switching between direct and connecting flights.



7. **🛠️ Backend Integration**:
   - Frontend communicates with the backend for real-time algorithm execution.
---

## 💻 Technologies Used

- **🖥️ Programming Language**: Python
- **📚 Libraries**:
  - **CustomTkinter**: For creating the GUI.
  - **TkinterMapView**: For visualizing maps and flight routes.
- **📊 Data Structures**: Graphs, KD-Trees
- **⚙️ Algorithms**: Dijkstra, A*, Bellman-Ford, DFS
- **🗂 Dataset Source**: OpenFlights (filtered for Asia region)

---

## ⚙️ Setup Instructions

1. **📥 Clone the Repository**:
   
```bash
   git clone https://github.com/your-username/flight-map-routing.git
```

2. **🗂 Requirements to run**:

```bash
pip install customtkinter
pip install tkintermapview
pip install geopy
pip install scipy
```


3. **▶️ Run the Application**:
```bash
   python main.py
```

---

## 💡 How to Use the App

- Run the app and enter the IATA code for your source and destination.
- Press "Search" (it may take awhile to search, depending on your system)
- After Searching, it will display the route on the map.
- Click on "Search Results" to view the results of the Algorithms
- This will also show the Flights (Direct and Connecting) for the chosen source and destionation.

---
## 🎥 **Project Presentation**

Watch our project presentation on YouTube: [Flight-Route Presentation](https://youtu.be/pJfiYvVBD50)

---

## 👥 Contributors

| **Name**                  | **SIT Student ID** | **SIT Email**                     |
|---------------------------|--------------------|-----------------------------------|
| Felix Chang               | 2301105           | 2301105@singaporetech.edu.sg     |
| Jiang Weimin              | 2301083           | 2301083@singaporetech.edu.sg     |
| Lim Jing Chuan Jonathan   | 2300923           | 2300923@singaporetech.edu.sg     |
| Tee Yu Cheng              | 2300884           | 2300884@singaporetech.edu.sg     |
| Elroy Lee                 | 2300950           | 2300950@singaporetech.edu.sg     |
| Ryan Oh Tian Guan         | 2300916           | 2300916@singaporetech.edu.sg     |
