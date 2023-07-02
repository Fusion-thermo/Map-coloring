from PIL import Image as Img #car Image existe déjà dans Tkinter et provoque des problèmes
from PIL import ImageTk
import numpy as np
from tkinter import *
import tkinter.filedialog
import networkx as nx
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, Binary, RangeSet

def rgb_to_hex(rgb):
    return '#'+'%02x%02x%02x' % rgb

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

couleurs=[(255,0,0),(0,255,0),(0,0,255),(219,20,255),(255,168,63),(0,255,255),(255,255,0)]
couleurs=[rgb_to_hex(i) for i in couleurs]

class Pixel:
    def __init__(self,x,y):
        self.x=x
        self.y=y

def Ouvrir():
    global matrice,hauteur,largeur, photo, picture, nodes, edges,numero_node, map # jsp pourquoi mais l'image "photo" ne s'affiche pas si elle n'est pas mise en global
    Canevas.delete(ALL)
    nodes={}
    edges=[]
    numero_node=0
    filename = tkinter.filedialog.askopenfilename(title="Ouvrir une image",filetypes=[('png files','.png'),('all files','.*')])
    #photo = PhotoImage(file=filename)
    map=Img.open(filename).convert("RGB")#convert RGB transforme les matrices n*m en n,m,3
    if "-clean" in filename:
        matrice=np.array(map)
        photo=ImageTk.PhotoImage(image=map)
    else:
        avancement.set("noir & blanc")
        map=noir_et_blanc(map)
        photo=ImageTk.PhotoImage(image=map)
        map.save(fp=filename[:filename.find(".")]+"-clean"+filename[filename.find("."):])
    avancement.set("Tracer le graphe")
    hauteur=photo.height()
    largeur=photo.width()
    picture=Canevas.create_image(0,0,anchor=NW,image=photo)
    Canevas.config(height=photo.height(),width=photo.width())
    fenetre.title("Image "+str(photo.width())+" x "+str(photo.height()))
    

def noir_et_blanc(image):
    global matrice
    #noir et blanc mais en mode rgb, donc pas de mode("1")
    matrice=np.array(image)
    largeur_ici,hauteur_ici=image.size

    for i in range(hauteur_ici):
        for j in range(largeur_ici):
            if (matrice[i,j] <240).all():
                matrice[i,j]=(0,0,0)
            else:
                matrice[i,j]=(255,255,255)
    image=Img.fromarray(matrice,"RGB")
    return image

def coloriage():
    recursif = fenetre.after(400,coloriage)
    global matrice, hauteur,largeur,picture, colors_map
    zone=colors_map[0]        
    #print("Zone {}/{}".format(colors_map.index(zone)+1,len(colors_map)))
    couleur=hex_to_rgb(zone[1])
    origine=Pixel(zone[0][1],zone[0][0])
    matrice[origine.x,origine.y] = couleur
    frontiere=[origine]
    avant=1
    if len(colors_map)==1:
        a=2

    while len(frontiere)>0:
        nouveau=[]
        for pixel in frontiere:
            if pixel.x+1<hauteur and (matrice[pixel.x+1,pixel.y] == 255).all():
                matrice[pixel.x + 1,pixel.y] = couleur
                nouveau.append(Pixel(pixel.x + 1,pixel.y))
            if pixel.y+1<largeur and (matrice[pixel.x,pixel.y + 1] == 255).all():
                matrice[pixel.x,pixel.y + 1] = couleur
                nouveau.append(Pixel(pixel.x,pixel.y + 1))
            if pixel.x-1>0 and (matrice[pixel.x - 1,pixel.y] == 255).all():
                matrice[pixel.x - 1,pixel.y] = couleur
                nouveau.append(Pixel(pixel.x - 1,pixel.y))
            if pixel.y-1>0 and (matrice[pixel.x,pixel.y - 1] == 255).all():
                matrice[pixel.x,pixel.y - 1] = couleur
                nouveau.append(Pixel(pixel.x,pixel.y - 1))
        frontiere=nouveau[:]
    colors_map.remove(zone)
    
    img=Img.fromarray(matrice,"RGB")
    picture=ImageTk.PhotoImage(image=img)
    Canevas.create_image(0,0,anchor=NW,image=picture)

    if len(colors_map)==0:
        fenetre.after_cancel(recursif)


def Clic_gauche(event):
    global x_clic, y_clic,node,edge_line,numero_node
    rayon=int(Rayon.get())
    x_clic=event.x
    y_clic=event.y
    nouveau=True
    for coos_node in nodes.keys():
        if (x_clic-coos_node[0])**2 + (y_clic-coos_node[1])**2 <= rayon**2:
            x_clic, y_clic=coos_node
            node=nodes[(x_clic,y_clic)]
            nouveau=False
    edge_line=Canevas.create_line(x_clic,y_clic,x_clic,y_clic,width=3)
    if nouveau:
        Canevas.create_oval(x_clic-rayon,y_clic-rayon,x_clic+rayon,y_clic+rayon,fill="red")
        nodes[(x_clic,y_clic)]=numero_node
        node=numero_node
        numero_node+=1
    
def Clic_gauche_survol(event):
    Canevas.coords(edge_line,x_clic,y_clic,event.x,event.y)

def Clic_gauche_release(event):
    global numero_node,node,x_clic, y_clic,nouveau_node,nodes,edges, edge_line, disque
    rayon=int(Rayon.get())
    x_save=x_clic
    y_save=y_clic
    x_clic=event.x
    y_clic=event.y
    nouveau_node=True
    for coos_node in nodes.keys():
        if (x_clic-coos_node[0])**2 + (y_clic-coos_node[1])**2 <= rayon**2:
            x_clic, y_clic=coos_node
            disque=Canevas.create_oval(x_clic-rayon,y_clic-rayon,x_clic+rayon,y_clic+rayon,fill="green")
            Canevas.coords(edge_line,x_save,y_save, x_clic,y_clic)
            if node != nodes[(x_clic, y_clic)]:
                edge=(node,nodes[(x_clic, y_clic)])
                edges.append(edge)
            nouveau_node=False
    if nouveau_node:
        disque=Canevas.create_oval(x_clic-rayon,y_clic-rayon,x_clic+rayon,y_clic+rayon,fill="green")
        nodes[(x_clic,y_clic)]=numero_node
        if node != numero_node:
            edge=(node,numero_node)
            edges.append(edge)
        numero_node+=1
    #print(nodes,edges)

def resolution_graphe(G):
     # Number of nodes
    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Create concrete model
    model = ConcreteModel()

    # Set of indices
    model.V = RangeSet(0, n-1)
    model.E = RangeSet(0, m-1)
    model.K = RangeSet(0, n-1)#nombre de couleurs=nombre de nodes au début

    # Variables
    model.x = Var(model.V, model.K, within=Binary)
    model.y = Var(model.K, within=Binary)

    # Objective Function
    #moins il y a de couleurs et mieux c'est, normalement max=4
    model.obj = Objective(expr=sum(model.y[k] for k in model.K))

    # Every node must  receive a single color
    def Unique(model, i):
        return sum(model.x[i, k] for k in model.K) == 1

    model.assign = Constraint(model.V, rule=Unique)

    # Conflict arcs
    #2 nodes must have different colors ?
    def Conflict(m, i, j, k):
        if (i,j) in G.edges():
            return m.x[i,k] + m.x[j,k] <= m.y[k]
        return Constraint.Skip

    model.conflict = Constraint(model.V, model.V, model.K, rule=Conflict)

    # Solve the model
    #sol = SolverFactory('gurobi').solve(model, tee=True)
    sol = SolverFactory('gurobi').solve(model)

    # CHECK SOLUTION STATUS

    # Get a JSON representation of the solution
    sol_json = sol.json_repn()
    # Check solution status
    if sol_json['Solver'][0]['Status'] != 'ok':
        return None
    if sol_json['Solver'][0]['Termination condition'] != 'optimal':
        return None

    sol = []
    for i in model.V:
        for k in model.K:
            if model.x[i,k]() == 1:
                sol.append( (i,k) )
    #print(model.obj(), sol)
    return model.obj(), sol

def resolution():
    global edges,colors_map,sol,nodes
    rayon=int(Rayon.get())
    avancement.set("Résolution")
    G.add_edges_from(edges)
    xhi, sol = resolution_graphe(G)
    n_couleurs.set(str(xhi)+" couleurs")

    #lister les couleurs possibles
    avancement.set("Coloriage")
    colors_lp=[]
    for i in sol:
        if i[1] not in colors_lp:
            colors_lp.append(i[1])
    #affecter à chaque coordonnée sa couleur
    colors_map=[]
    for i in sol:
        for coos in nodes.keys():
            if nodes[coos]==i[0]:
                colors_map.append((coos,couleurs[colors_lp.index(i[1])]))
    #colorier la carte
    for point in colors_map:
        Canevas.create_oval(point[0][0]-rayon,point[0][1]-rayon,point[0][0]+rayon,point[0][1]+rayon,fill=point[1])


def erreur_node():
    global numero_node
    edges.pop() #edge entre les deux nodes
    Canevas.delete(edge_line) #trait entre les deux nodes
    Canevas.delete(disque) #disque 
    numero_node-=1
    for clef in nodes.keys():
        if nodes[clef]==numero_node:
            del nodes[clef]#node
            break

def reset_carte():
    global nodes, edges, numero_node, photo, matrice
    Canevas.delete(ALL)
    nodes={}
    edges=[]
    numero_node=0
    matrice=np.array(map)
    Canevas.create_image(0,0,anchor=NW,image=photo)

fenetre=Tk()

Canevas=Canvas(fenetre, height=300, width=300)
Canevas.pack(side=LEFT)

Canevas.bind('<Button-1>',  Clic_gauche)
Canevas.bind('<B1-Motion>',  Clic_gauche_survol)
Canevas.bind('<ButtonRelease-1>',  Clic_gauche_release)

bouton_resolution = Button(fenetre,  text = 'Résoudre',  command = resolution)
bouton_resolution.pack()

bouton_coloriage = Button(fenetre,  text = 'Coloriage',  command = coloriage)
bouton_coloriage.pack()

bouton_erreur = Button(fenetre,  text = 'Erreur node',  command = erreur_node)
bouton_erreur.pack()

bouton_reset = Button(fenetre,  text = 'Reset carte',  command = reset_carte)
bouton_reset.pack()

Rayon=StringVar()
Rayon.set(7)
rayon_scale=Scale(fenetre,  orient='horizontal',  from_=1,  to=15,  resolution=1, tickinterval=5,  label='Rayon',  variable=Rayon)
rayon_scale.pack(side="top")

Bouton1 = Button(fenetre,  text = 'Quitter',  command = fenetre.destroy)
Bouton1.pack()

menubar = Menu(fenetre)
menufichier = Menu(menubar,tearoff=0)
menufichier.add_command(label="Ouvrir une image",command=Ouvrir)
menubar.add_cascade(label="Fichier", menu=menufichier)
fenetre.config(menu=menubar)

avancement=StringVar()
Label(fenetre,textvariable=avancement).pack()
avancement.set("En attente")

n_couleurs=StringVar()
Label(fenetre,textvariable=n_couleurs).pack()
n_couleurs.set("")

G=nx.Graph()

fenetre.mainloop()