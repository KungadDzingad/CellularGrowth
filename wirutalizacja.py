import numpy as np
import random
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import os
import glob


FOLDER = "growth"

class GUI():
    def __init__(self):
        self.width = 600
        self.height = 600

        self.growth = None
        
        self.root = tk.Tk()
        self.main = tk.Canvas(self.root, width=650, height=600)


        self.image_panel = tk.Canvas(self.root,width=600,height=600,bg="white")
        self.image_panel.pack(side="left")

        self.canvas_panel = tk.Frame(self.root, width=100, height=600)
        self.canvas_panel.pack(side="right")

        self.image = Image.new("RGB",(600, 600), (255,255,255))
        self.tkimage = None

        self.x_label = tk.Label(self.canvas_panel, text="X: ")
        self.x_label.pack()
        self.x_entry = tk.Entry(self.canvas_panel)
        self.x_entry.pack()

        self.y_label = tk.Label(self.canvas_panel, text="Y: ")
        self.y_label.pack()
        self.y_entry = tk.Entry(self.canvas_panel)
        self.y_entry.pack()

        self.meth_val = tk.StringVar()
        self.meth_label= tk.Label(self.canvas_panel,text="Method: ")
        self.meth_label.pack()
        self.meth_cmb = ttk.Combobox(self.canvas_panel,textvariable=self.meth_val)
        self.meth_cmb.pack()
        self.meth_cmb['values'] = ('Monte Carlo', 'CA')

        self.nuc_val = tk.StringVar()
        self.nuc_label= tk.Label(self.canvas_panel,text="Nucleation: ")
        self.nuc_label.pack()
        self.nuc_cmb = ttk.Combobox(self.canvas_panel,textvariable=self.nuc_val)
        self.nuc_cmb.pack()
        self.nuc_cmb['values'] = ('Random', 'Homogenous')


        self.grow_val = tk.StringVar()
        self.grow_label= tk.Label(self.canvas_panel,text="Growth: ")
        self.grow_label.pack()
        self.grow_cmb = ttk.Combobox(self.canvas_panel,textvariable=self.grow_val)
        self.grow_cmb.pack()
        self.grow_cmb['values'] = ('Neumann', 'Pentagonal')

        self.bndr_val = tk.StringVar()
        self.bndr_label= tk.Label(self.canvas_panel,text="Nucleation: ")
        self.bndr_label.pack()
        self.bndr_cmb = ttk.Combobox(self.canvas_panel,textvariable=self.bndr_val)
        self.bndr_cmb.pack()
        self.bndr_cmb['values'] = ('Transition', 'Absorbing')

        
        self.g_label = tk.Label(self.canvas_panel, text="Grains (RANDOM), Gap (HOMOGENOUS): ")
        self.g_label.pack()
        self.g_entry = tk.Entry(self.canvas_panel)
        self.g_entry.pack()



        self.start_btn = tk.Button(self.canvas_panel, text="Start",command= lambda : self.start())
        self.start_btn.pack()

        self.create_folder()
        self.root.mainloop()



    def start(self):
        width = int(self.x_entry.get())
        height = int(self.y_entry.get())
        g = int(self.g_entry.get())
        method = self.meth_val.get()
        nucleation = self.nuc_val.get()
        growth = self.grow_val.get()
        boundary = self.bndr_val.get()

        self.growth = Growth(method,nucleation, growth, boundary,g,width,height,self)
        self.growth.start()

    def paint_canvas(self,step):
        pixels = self.image.load()
        w = len(self.growth.cells[0])
        h = len(self.growth.cells)

        cell_width = int( self.width/ w)
        cell_height = int( self.height / h)

    
        for cell in self.growth.c_list:
            for i in range(cell_width):
                for j in range(cell_height):
                    if cell.id != 0:
                        pixels[cell.x*cell_width+ i, cell.y*cell_height + j] = self.growth.get_cell_coloring(cell)
                        
        self.image.save("{}/{}{}.png".format(FOLDER, FOLDER, step))


    def show_final_result_in_gui(self,step):
        self.tkimage = ImageTk.PhotoImage(Image.open(f"{FOLDER}/{FOLDER}{step}.png"))
        self.image_panel.create_image(0,0,anchor="nw",image=self.tkimage)

    def create_folder(self):
        path = os.path.join(os.getcwd(),FOLDER)
        if not os.path.exists(path):
            os.mkdir(path)
        files = glob.glob(f'{FOLDER}/*')
        for f in files:
            os.remove(f)

class Cell():
    def __init__(self, id, x, y):
        self.id = id 
        self.x = x
        self.y = y

    def __repr__(self) :
        return f"({self.id},{self.x},{self.y})"


class Growth():
    def __init__(self, method, nucleation, growth, boundary, grain_size, width, height, gui: GUI):
        self.method = method
        self.nucleation = nucleation
        self.growth = growth
        self.boundary = boundary
        self.x = width
        self.y = height
        self.g_size = grain_size
        self.grains = []
        self.c_list = []
        
        
        self.cells = None

        self.gui = gui


    def get_cell_coloring(self, cell : Cell):
        return self.grains[cell.id - 1]

    def start(self):
        if self.method == "CA":
            self.CA()
        else:
            self.monte_carlo()


    def generate_grains(self):     
        self.grains = []
        for g in range(self.g_size):
            while True:
                grain = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                if grain not in self.grains:
                    self.grains.append(grain)
                    break


    def CA(self):
        self.generate_grains()
        self.cells = self.generate_cells()
        nuc_cells = self.nucleation_ca()

        neighbours = set()

        for cell in nuc_cells:
            neighbours = neighbours.union(self.get_neighbours(cell))
        neighbours = set([n for n in neighbours if n.id == 0])

        i = 0
        self.update(0)
        while any(c.id == 0 for c in self.c_list):
            new_neighbours = set()
            i += 1
            for neighbour in neighbours:
                ns = self.color_cell_and_return_empty_neighbours(neighbour)
                new_neighbours = new_neighbours.union(ns)
            neighbours.clear()
            neighbours = neighbours.union(new_neighbours)
            self.update(i)

        self.gui.show_final_result_in_gui(i)

    def monte_carlo(self):
        self.generate_grains()
        self.cells = self.generate_cells()
        self.nucleation_m_c()

        self.update(0)

        for i in range(40):
            for cell in self.c_list:
                self.change_color_by_energy(cell)      
            self.update(i+1)

        self.gui.show_final_result_in_gui(i)

    def nucleation_m_c(self):
        for cell in self.c_list:
            grain = random.randint(1,len(self.grains))
            cell.id = grain



    def change_color_by_energy(self, cell):
        neighbours = self.get_neighbours(cell) 
        energy = self.get_cell_energy(cell.id,neighbours)
        new_id = random.choice(list(neighbours)).id
        delta_energy = energy - self.get_cell_energy(new_id,neighbours)

        if delta_energy > 0:
            cell.id = new_id
        

    def get_cell_energy(self, id, neighbours):
        energy = 0
        for neigh in neighbours:
            if neigh.id != id:
                energy += 1
        return energy
    
    def update(self, step):
        self.gui.paint_canvas(step)


    def color_cell_and_return_empty_neighbours(self, cell):
        neighbours = self.get_neighbours(cell)
        empty_neighbours = [n for n in neighbours if n.id == 0]
        check_neighbours = [n for n in neighbours if n.id != 0]
        
        # time.sleep(5)
        id_count = {}
        for n in check_neighbours:
            if n.id in id_count.keys():
                id_count[n.id] += 1
            else :
                id_count[n.id] = 1

        max_ids = [k for k, v in id_count.items() if v == max(id_count.values())]
        if len(max_ids) > 0:
            cell.id = random.choice(max_ids)

        return empty_neighbours


    
    def nucleation_ca(self):
        nuc_cells = set()

        if self.nucleation == "Random":
            for grain in self.grains:
                while True:
                    x = random.randint(1,self.x-2)
                    y = random.randint(1,self.y-2)
                    if self.cells[x][y].id == 0:
                        self.cells[x][y].id = self.grains.index(grain) + 1
                        nuc_cells.add(self.cells[x][y])
                        break
        else:

            offset = self.g_size
            offset_x = int((self.x -2) / offset)
            offset_y = int((self.y - 2) / offset)
            self.g_size = offset_x*offset_y
            self.generate_grains()

            grain_nr = 1
            for j in range(offset):
                for i in range(offset):
                   if j*(offset_x+1) + 1  < self.x-1 and i*(offset_y+1) + 1 < self.y-1:
                        self.cells[j*(offset_x+1) + int(offset_x /2)][i*(offset_y+1) + int(offset_y/2)].id = grain_nr
                        grain_nr += 1
                        nuc_cells.add(self.cells[j*(offset_x+1) + int(offset_x/2)][i*(offset_y+1) + int(offset_y/2)])
            
            


        return nuc_cells

    
    def get_neighbours(self,cell : Cell):
        neighbours = set()
        index = self.c_list.index(cell)

        
        
        if self.boundary == "Absorbing":
            if self.growth == "Neumann":
                
                try:
                    neighbours.add(next(c for c in self.c_list if cell.x-1 == c.x and cell.y == c.y ))
                except: pass
            
                try:
                    neighbours.add(next(c for c in self.c_list if cell.x == c.x and cell.y -1 == c.y))
                except: pass
            
                try:
                    neighbours.add(next(c for c in self.c_list if cell.x+1 == c.x and cell.y == c.y ))
                except: pass
            
                try:
                    neighbours.add(next(c for c in self.c_list if cell.x == c.x and cell.y+1 == c.y ))
                except: pass
            else:

                rand = random.randint(1,4)

                if rand == 1: #down
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x+1 == c.x and cell.y == c.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x+1 == c.x and cell.y+1 == c.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x == c.x and cell.y +1 == c.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x-1 == c.x and cell.y +1 == c.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x-1 == c.x and cell.y == c.y ))
                    except: pass
                elif rand == 2: #left
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y+1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x - 1 == c.x and  c.y == cell.y+1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x - 1 == c.x and  c.y == cell.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x -1  == c.x and  c.y == cell.y-1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y-1 ))
                    except: pass
                elif rand == 3: #up
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x -1 == c.x and  c.y == cell.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x - 1 == c.x and  c.y == cell.y-1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y -1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x +1  == c.x and  c.y == cell.y-1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x  +1 == c.x and  c.y == cell.y ))
                    except: pass
                elif rand == 4: #right
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y-1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x + 1 == c.x and  c.y == cell.y-1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x + 1 == c.x and  c.y == cell.y ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x + 1  == c.x and  c.y == cell.y+1 ))
                    except: pass
                    try:
                        neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y+1 ))
                    except: pass
              
        else:
            if self.growth == "Neumann":
                offset_x = [1,1]
                offset_y = [1,1]

                if cell.x == 0:
                    offset_x[1] = -(self.x - 1)
                if cell.y == 0:
                    offset_y[1] = -(self.y - 1)
                if cell.x == self.x-1:
                    offset_x[0] = -(self.x - 1)
                if cell.y == self.y-1:
                    offset_y[0] = -(self.y - 1)                
            
                neighbours.add(next(c for c in self.c_list if cell.x-offset_x[1] == c.x and cell.y == c.y ))
                neighbours.add(next(c for c in self.c_list if cell.x == c.x and cell.y -offset_y[1] == c.y))
                neighbours.add(next(c for c in self.c_list if cell.x+offset_x[0] == c.x and cell.y == c.y ))           
                neighbours.add(next(c for c in self.c_list if cell.x == c.x and cell.y+offset_y[0] == c.y ))
                
               
            else:

                rand = random.randint(1,4)
                offset_x = [1,1]
                offset_y = [1,1]

                if cell.x == 0:
                    offset_x[1] = -(self.x - 1)
                if cell.y == 0:
                    offset_y[1] = -(self.y - 1)
                if cell.x == self.x-1:
                    offset_x[0] = -(self.x - 1)
                if cell.y == self.y-1:
                    offset_y[0] = -(self.y - 1)

                if rand == 1: #down
                    
                    neighbours.add(next(c for c in self.c_list if cell.x+offset_x[0] == c.x and cell.y == c.y ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x+offset_x[0] == c.x and cell.y+offset_y[0] == c.y ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x == c.x and cell.y +offset_y[0] == c.y ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x-offset_x[1]== c.x and cell.y +offset_y[0] == c.y ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x-offset_x[1] == c.x and cell.y == c.y ))
                
                elif rand == 2: #left
                   
                    neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y+offset_y[0] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x - offset_x[1] == c.x and  c.y == cell.y+offset_y[0] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x - offset_x[1] == c.x and  c.y == cell.y ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x - offset_x[1]  == c.x and  c.y == cell.y-offset_y[1] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y-offset_y[1] ))
                    
                elif rand == 3: #up
                   
                    neighbours.add(next(c for c in self.c_list if cell.x - offset_x[1] == c.x and  c.y == cell.y ))
                
                
                    neighbours.add(next(c for c in self.c_list if cell.x - offset_x[1] == c.x and  c.y == cell.y-offset_y[1] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y -offset_y[1] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x + offset_x[0]  == c.x and  c.y == cell.y-offset_y[1] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x  + offset_x[0] == c.x and  c.y == cell.y ))
                    
                elif rand == 4: #right
                   
                    neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y-offset_y[1] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x + offset_x[0] == c.x and  c.y == cell.y-offset_y[1] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x + offset_x[0] == c.x and  c.y == cell.y ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x + offset_x[0]  == c.x and  c.y == cell.y+offset_y[0] ))
                
                    neighbours.add(next(c for c in self.c_list if cell.x  == c.x and  c.y == cell.y+offset_y[0] ))
                    
           
        print(neighbours)
        return neighbours

    def generate_cells(self):
        self.c_list = []
        generated_cells = []
        for i in range(self.x):
            inner_list = []
            for j in range(self.y):
                cell = Cell(0,j,i)
                inner_list.append(cell)
                self.c_list.append(cell)
            generated_cells.append(inner_list)
        return generated_cells

    
    def get_cells_list(self):
        return np.array(self.cells).flatten().tolist()




GUI()