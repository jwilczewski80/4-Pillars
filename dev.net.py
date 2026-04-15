import requests
import urllib.parse
import tkinter as tk
from tkinter import messagebox

# this sets up the window dimensions
root = tk.Tk()
root.geometry("600x900")
root.title("GPS")
root.configure(background="light blue")

#this will set up the border for the information
appFrame = tk.Frame(root, padx=20,pady=40)
appFrame.pack(padx=20,pady=40,fill=tk.BOTH, expand=True)
appFrame.configure(background="light green")

headerLabel = tk.Label(
    appFrame,
    text="GPS Route Planner",
    font=("Arial", 20, "bold"),
    bg="light green"
)
headerLabel.grid(row=0, column=0, columnspan=3, pady=10)

#this sets up the labels for the input blocks
startLocation = tk.Label(appFrame, text="Starting location:")
startLocation.grid(row=1,column=0, sticky=tk.W)
startLocationInput = tk.Entry(appFrame)
startLocationInput.grid(row=1, column=1,padx=20,pady=0)

stop1Location = tk.Label(appFrame, text="Stop 1:")
stop1Location.grid(row=2,column=0, sticky=tk.W)
stop1LocationInput = tk.Entry(appFrame)
stop1LocationInput.grid(row=2,column=1,padx=20,pady=5)

stop2Location = tk.Label(appFrame, text="Stop 2:")
stop2Location.grid(row=3,column=0, sticky=tk.W)
stop2LocationInput = tk.Entry(appFrame)
stop2LocationInput.grid(row=3,column=1,padx=20,pady=5)

stop3Location = tk.Label(appFrame, text="Final Destination:")
stop3Location.grid(row=4,column=0, sticky=tk.W)
stop3LocationInput = tk.Entry(appFrame)
stop3LocationInput.grid(row=4,column=1,padx=20,pady=5)


route_url = "https://graphhopper.com/api/1/route?"
mode = "car"

#output display setup
answer = tk.Text(appFrame, state="disabled")
answer.grid(row=7, column=0, columnspan=3, pady=20, sticky="nsew")
appFrame.grid_rowconfigure(7, weight=1)
appFrame.grid_columnconfigure(1, weight=1)

key = "257d99b4-a47b-40f5-8301-befc94c854af"

#prints onto the GUI
def printOnGUI(*args, sep=" ", end="\n"):
    text = sep.join(map(str,args)) + end
    answer.config(state="normal")
    answer.insert("end",text)
    answer.config(state="disabled")

#Runs normal distance calculations
def calculate():
    answer.config(state="normal")
    answer.delete('1.0', "end")
    answer.config(state="disabled")

    locations = [
        startLocationInput.get(),
        stop1LocationInput.get(),
        stop2LocationInput.get(),
        stop3LocationInput.get()
    ]

    locations = [loc.strip() for loc in locations if loc.strip() != ""]

    if len(locations) < 2:
        messagebox.showerror("Input Error", "Please enter a starting location and at least one stop.")
        return
    
    printOnGUI("=================================================")
    printOnGUI("Final Destination: " + locations[-1])
    printOnGUI("=================================================")

    total_miles = 0
    total_time = 0

    printOnGUI("=================================================")

    for i in range(len(locations) - 1):
        currentStart = locations[i]
        currentStop = locations[i + 1]

        init = geocoding(currentStart, key)
        stop = geocoding(currentStop, key)

        if init[0] == 200 and stop[0] == 200:
            op = "&point=" + str(init[1]) + "%2C" + str(init[2])
            dp = "&point=" + str(stop[1]) + "%2C" + str(stop[2])

            paths_url = route_url + urllib.parse.urlencode({"key":key, "vehicle":mode}) + op + dp

            response = requests.get(paths_url)
            paths_status = response.status_code
            paths_data = response.json()

            printOnGUI("Routing API Status: " + str(paths_status))
            printOnGUI("Directions from " + init[3] + " to " + stop[3] + " by " + mode)
            printOnGUI("=================================================")

            if paths_status == 200:
                miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
                trip_time = paths_data["paths"][0]["time"]

                total_miles += miles
                total_time += trip_time

                sec = int(trip_time / 1000 % 60)
                min = int(trip_time / 1000 / 60 % 60)
                hr = int(trip_time / 1000 / 60 / 60)

                printOnGUI("Distance Traveled: {0:.1f} miles".format(miles))
                printOnGUI("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
                printOnGUI("-------------------------------------------------")

                for each in range(len(paths_data["paths"][0]["instructions"])):
                    path = paths_data["paths"][0]["instructions"][each]["text"]
                    distance = paths_data["paths"][0]["instructions"][each]["distance"]
                    printOnGUI("{0} ( {1:.1f} miles )".format(
                        path, distance / 1000 / 1.61))

                printOnGUI("=================================================")
            else:
                printOnGUI("Error message: " + paths_data["message"])
                printOnGUI("*************************************************")
                return
        else:
            messagebox.showerror("Geocoding Error", "One of the locations could not be found.")
            return

    total_sec = int(total_time / 1000 % 60)
    total_min = int(total_time / 1000 / 60 % 60)
    total_hr = int(total_time / 1000 / 60 / 60)

    printOnGUI("TOTAL TRIP")
    printOnGUI("Distance Traveled: {0:.1f} miles".format(total_miles))
    printOnGUI("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(total_hr, total_min, total_sec))
    printOnGUI("=================================================")

#Uses the API to gather geographical information
def geocoding (location, key):
    if location == "":
     return 400, "null", "null", location
    geocode_url = "https://graphhopper.com/api/1/geocode?" 
    url = geocode_url + urllib.parse.urlencode({"q":location, "limit": "1", "key":key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    if json_status == 200 and len(json_data["hits"]) !=0:
        lat=(json_data["hits"][0]["point"]["lat"])
        lng=(json_data["hits"][0]["point"]["lng"])
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        
        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country=""
        
        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state=""
        
        if len(state) !=0 and len(country) !=0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) !=0:
            new_loc = name + ", " + country
        else:
            new_loc = name
        
        print("Geocoding API URL for " + new_loc + " (Location Type: " + value + ")\n" + url)
    else:
        lat="null"
        lng="null"
        new_loc=location
        if json_status != 200:
            print("Geocode API status: " + str(json_status) + "\nError message: " + json_data["message"])
    return json_status,lat,lng,new_loc



#confirm choices
calcButton = tk.Button(appFrame, text = "Calculate", command=calculate)
calcButton.grid(row=6, column=1, padx=20, pady=20)

def setCar():
    global mode
    mode = "car"

def setBike():
    global mode
    mode = "bike"

def setFoot():
    global mode
    mode = "foot"

#transportation choices
carButton = tk.Button(appFrame, text = "Car", command=setCar)
carButton.grid(row=5, column=0)
bikeButton = tk.Button(appFrame, text = "Bike", command=setBike)
bikeButton.grid(row=5, column=1)
footButton = tk.Button(appFrame, text = "Foot", command=setFoot)
footButton.grid(row=5,column=2)

#tkinter main loop
root.mainloop()

