from Tkinter import *
import ttk
from PIL import ImageTk, Image
from clusters import *
import tkFileDialog
import clusters

# Checking for EOF retrieved from https://stackabuse.com/reading-files-with-python/

class ElectionCluster(Frame):
    def __init__(self, parent):  # Initializing the UI
        Frame.__init__(self)
        self.initUI()
        self.data_center = DataCenter()  # Creating the data center where all data is kept
        self.var = StringVar()  # Creating variable for keeping track of which clustering type is chosen, uused for refine analysis
        self.var.set("a")
        self.run = 0  # Keeping track of whether it is the first run or not, used for GUI initializing

    def initUI(self):  # Here all the initial parts of the GUI are created
        self.label_title = Label(text="Election Data Analysis Tool", font=("", "20", "bold"), fg="white", bg="red")
        self.label_title.pack(fill=X)
        self.button_load_data = Button(text="Load Election Data", command=self.load_data, width=30, height=2, bg="lightgrey", relief=RIDGE)
        self.button_load_data.pack(pady=10)
        self.frame_buttons  = Frame()
        self.frame_buttons.pack()
        self.button_cluster_dist = Button(self.frame_buttons, text="Cluster Districts", width=30, height=2, bg="lightgrey", relief=RIDGE)
        self.button_cluster_dist.bind("<Button-1>", self.cluster_dist)
        self.button_cluster_dist.pack(side=LEFT)
        self.button_cluster_poli = Button(self.frame_buttons, text="Cluster Political Parties", width=30, height=2, bg="lightgrey", relief=RIDGE)
        self.button_cluster_poli.bind("<Button-1>", self.cluster_poli)
        self.button_cluster_poli.pack()
        self.frame_canvas = Frame()
        self.frame_canvas.pack(pady=10)
        self.frame_bottom = Frame()  # Frame for the part of the GUI that is created after a cluster button is pressed
        self.frame_bottom.pack()
        self.pack(fill=BOTH)

    def create_rest_of_gui(self):  # Creates the rest of the GUI after a clustering button is pressed
        for widget in self.frame_canvas.winfo_children():  # These two for loops clear the widgets that existed before since we want to reset the after each clustering
            widget.destroy()
        for widget in self.frame_bottom.winfo_children():
            widget.destroy()
        self.canvas = Canvas(self.frame_canvas, bg="white", height=400, width=1000, scrollregion=(0, 0, 1200, 780))  # Canvas that will hold the cluster dendogram
        self.hbar = Scrollbar(self.frame_canvas, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = Scrollbar(self.frame_canvas, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack()
        self.label_dist = Label(self.frame_bottom, text="Districts:")
        self.label_dist.pack(side=LEFT)
        self.frame_lb = Frame(self.frame_bottom)
        self.frame_lb.pack(side=LEFT)
        self.scroll_lb = Scrollbar(self.frame_lb)
        self.scroll_lb.pack(side=RIGHT, fill=Y)
        self.lb = Listbox(self.frame_lb, yscrollcommand=self.scroll_lb.set, selectmode="multiple")
        self.lb.pack(side=LEFT)
        self.scroll_lb.configure(command=self.lb.yview)
        for district in self.data_center.list_of_districts:  # Inserts the districts into the listbox
            self.lb.insert(END, district)
        self.label_thresh = Label(self.frame_bottom, text="Threshold:")
        self.label_thresh.pack(side=LEFT)
        self.combobox = ttk.Combobox(self.frame_bottom, state="readonly", values=["0%", "1%", "10%", "20%", "30%", "40%" ,"50%"], width=5)
        self.combobox.pack(side=LEFT)
        self.combobox.current(0)
        self.button_ref_analysis = Button(self.frame_bottom, text="Refine Analysis", width=30, height=2, bg="lightgrey", relief=RIDGE)
        self.button_ref_analysis.bind("<Button-1>", self.cluster_refined)
        self.button_ref_analysis.pack(side=LEFT)
        self.pack(fill=BOTH)

    def load_data(self):
        self.data_center.RnP_elec_data()  # Calls a method from DataCenter class to read and parse the election file

    def cluster_refined(self, event):  # Calls one of the clustering methods according to what the variable is
        var = self.var.get()  # Variable is set to to last pressed clustering type since we want just to refine the before existing result
        if var == "district":
            self.cluster_dist(event)
        elif var == "party":
            self.cluster_poli(event)

    def create_matrix(self):
        matrix = []  # List that will hold the matrix
        threshold = float(self.combobox.get()[:-1])  # Gets the thershold from the combobox
        self.selected_districts = [self.lb.get(i) for i in self.lb.curselection()]  # appends the districts that are selected in the listbox
        if self.selected_districts == []:  # if no disticts are selected in the listbox adds all districts to the list for clustering
            self.selected_districts = self.data_center.list_of_districts
        parties = self.data_center.list_of_parties  # Gets all the political parties from DataCenter
        for party_acr in parties:
            list_for_party = []  # Holds one of the rows of the matrix
            for district in self.selected_districts:
                try:
                    if float(self.data_center.parties_dict[party_acr].election_results[district]) >= threshold:  # filters out parties from disttricts whose vote percentage are below threshold
                        list_for_party.append(float(self.data_center.parties_dict[party_acr].election_results[district]))
                    else:
                        list_for_party.append(0.0)
                except KeyError:
                    list_for_party.append(0.0)  # If the party isn't available in a certain district sets the vote percentage to 0
            matrix.append(list_for_party)
        matrix = clusters.rotatematrix(matrix)
        return matrix

    def cluster_dist(self, event):  # function to cluster according to districts
        if self.run == 0:  # checks if it is the first time that clustering has been made
            self.create_rest_of_gui()
            self.run += 1
        self.update_idletasks()
        self.var.set("district")  # sets the variable for usage in refined analysis
        clust = clusters.hcluster(self.create_matrix(), distance=sim_distance)  # calls a function from clusters.py to do the clustering
        clusters.drawdendrogram(clust, self.selected_districts)  # calls a function from clusters.py to draw the dendogram
        self.create_rest_of_gui()  # recreates the 2. GUI part so everything is reset
        self.img = ImageTk.PhotoImage(Image.open("clusters.jpg"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.img)  # Inserts the dendogram to the canvas

    def cluster_poli(self, event):  # function to cluster according to parties
        if self.run == 0:  # checks if it is the first time that clustering has been made
            self.create_rest_of_gui()
            self.run += 1
        self.update_idletasks()
        self.var.set("party")  # sets the variable for usage in refined analysis
        clust = clusters.hcluster(clusters.rotatematrix(self.create_matrix()), distance=sim_distance)  # calls a function from clusters.py to do the clustering
        clusters.drawdendrogram(clust, self.data_center.list_of_parties)  # calls a function from clusters.py to draw the dendogram
        self.create_rest_of_gui()  # recreates the 2. GUI part so everything is reset
        self.img = ImageTk.PhotoImage(Image.open("clusters.jpg"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.img)  # Inserts the dendogram to the canvas


class DataCenter:  # Class that represents the data center, all of the information is hold here
    def __init__(self):
        self.districts_dict = {}  # dictionary for holding the districts
        self.parties_dict = {}  # dictionary for holding the parties

    def RnP_elec_data(self):  # opens file browser to select a file, loads it and parses it
        self.election_data_file = tkFileDialog.askopenfilename(
            initialdir="C:\Users\Yunus Stahlschmidt\PycharmProjects\ENGR 102\MP 3",
            title="Choose File", filetypes=(("txt Files", "*.txt"), ("all files", "*.*")))
        with open(self.election_data_file) as file:
            while True:
                line = file.readline()  # Checks for EOF (taken from stackabuse.com)
                if not line:
                    break
                my_district = file.readline()[:-1]
                my_district = District(my_district)  # reads the district name and initializes a District object
                for i in range(6):
                    file.readline()
                while True:
                    buffer = file.readline()  # assings the line to a variable for further processing
                    if buffer.startswith("Toplam"):
                        for i in range(2):
                            file.readline()  # Skips to the next "Kaynak"
                        break
                    if buffer.startswith("BGMSZ"):  # Skips the independent parties
                        continue
                    else:
                        my_list = buffer.split('\t')  # holds a of the information in a line, the necessary info will be retrieved from this
                        my_2_list = []
                        my_2_list.append(my_list[0])
                        my_2_list.append(my_list[-1][1:-1])
                        my_district.election_results[my_2_list[0]] = my_2_list[1]
                        self.districts_dict[my_district.name] = my_district
                        if my_2_list[0] not in self.parties_dict:
                            my_party = Party(my_2_list[0])
                            my_party.election_results[my_district.name] = my_2_list[1]
                            self.parties_dict[my_2_list[0]] = my_party
                        elif my_2_list[0] in self.parties_dict:
                            self.parties_dict[my_2_list[0]].election_results[my_district.name] = my_2_list[1]

        self.list_of_districts = self.districts_dict.keys()
        self.list_of_districts.sort()  # for inserting the districts to the listbox in alphabetical order and that we have an order in clustering
        self.list_of_parties = self.parties_dict.keys()  # holds the names of the parties for clustering


class District:  # class that represents each district object
    def __init__(self, name):
        self.name = name
        self.election_results = {}  # holds all of the info for each district


class Party:  # class that represents each party object
    def __init__(self, acronym):
        self.acronym = acronym
        self.election_results = {}  # holds all of the info for each party


root = Tk()
root.title("Clustering")
root.geometry("1100x900+500+0")
app = ElectionCluster(root)
root.mainloop()
