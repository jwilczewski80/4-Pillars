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

#this sets up the labels for the input blocks
startLocation = tk.Label(appFrame, text="Starting location:")
startLocation.grid(row=0,column=0, sticky=tk.W)
startLocationInput = tk.Entry(appFrame)
startLocationInput.grid(row=0,column=1,padx=20,pady=0)

stopLocation = tk.Label(appFrame, text="Stop location:")
stopLocation.grid(row=1,column=0, sticky=tk.W)
stopLocationInput = tk.Entry(appFrame)
stopLocationInput.grid(row=1,column=1,padx=20,pady=5)

route_url = "https://graphhopper.com/api/1/route?"
mode = "car"
#output display setup
answer = tk.Text(root, state="disabled")
answer.pack(fill="both",expand = True)

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
    startLocation1 = startLocationInput.get()
    stopLocation1 = stopLocationInput.get()
    init = geocoding(startLocation1, key)
    stop1 = geocoding(stopLocation1, key)
    printOnGUI("=================================================")
    if init[0] == 200 and stop1[0] == 200:
        op="&point="+str(init[1])+"%2C"+str(init[2])
        dp="&point="+str(stop1[1])+"%2C"+str(stop1[2])
        paths_url = route_url + urllib.parse.urlencode({"key":key, "vehicle":mode}) + op + dp
        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()
        printOnGUI("Routing API Status: " + str(paths_status) + "\nRouting API URL:\n" + paths_url)
        printOnGUI("=================================================")
        printOnGUI("Directions from " + init[3] + " to " + stop1[3] + " by " + mode)
        printOnGUI("=================================================")
        if paths_status == 200:
            miles = (paths_data["paths"][0]["distance"])/1000/1.61
            km = (paths_data["paths"][0]["distance"])/1000
            sec = int(paths_data["paths"][0]["time"]/1000%60)
            min = int(paths_data["paths"][0]["time"]/1000/60%60)
            hr = int(paths_data["paths"][0]["time"]/1000/60/60)
            printOnGUI("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
            printOnGUI("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            printOnGUI("=================================================")
            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                printOnGUI("{0} ( {1:.1f} km / {2:.1f} miles )".format(path, distance/1000, distance/1000/1.61))
            printOnGUI("=============================================")
        else:
            printOnGUI("Error message: " + paths_data["message"])
            printOnGUI("*************************************************")

#Uses the API to gather geographical information
def geocoding (location, key):
    while location == "":
        location = input("Enter the location again: ")
    geocode_url = "https://graphhopper.com/api/1/geocode?" 
    url = geocode_url + urllib.parse.urlencode({"q":location, "limit": "1", "key":key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    if json_status == 200 and len(json_data["hits"]) !=0:
        json_data = requests.get(url).json()
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
calcButton = tk.Button(appFrame, text = "calculate", command=calculate)
calcButton.grid(row=4,padx=20,pady=50)

def setCar():
    mode = "car"

def setBike():
    mode = "bike"

def setFoot():
    mode = "foot"

#transportation choices
carButton = tk.Button(appFrame, text = "car", command = setCar)
carButton.grid(row=3)
bikeButton = tk.Button(appFrame, text = "bike", command = setBike)
bikeButton.grid(row=3, column=1)
footButton = tk.Button(appFrame, text = "foot", command=setFoot)
footButton.grid(row=3,column=2)

#tkinter main loop
root.mainloop()


