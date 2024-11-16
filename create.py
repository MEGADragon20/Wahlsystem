import json
import random as r

def generate_verif_code(passport_id = str):
    code = ""
    for i in range(16):
        code += r.choice(["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9" ])
    with open("data/verif.json", 'r') as file:
        data = json.load(file)
    data[passport_id] = {"verif-code": code, "voted": False}
    overwrite(data)

def preset(IDs = list):
    for i in IDs:
        generate_verif_code(i)

def overwrite(data):
    with open("data/verif.json", 'w') as file:
        json.dump(data, file, ensure_ascii= False, indent=4)


preset([
"T2200015",
 "K3500023",
   "C4100067",
     "T2800011",
       "K1400054",
         "C3900002",
           "T1100029",
             "K2400018",
               "C3000072",
                 "T2100060",
"K1900046",
 "C3300008",
   "T1200034",
     "K2200081",
       "C4200059",
         "T1800027",
           "K3700061",
             "C4000019",
               "T2500033",
                 "K1300079",
"C4400090",
 "T2700012",
   "K1600055",
     "C3200068",
       "T1400047",
         "K2300036",
           "C3600073",
             "T1000088",
               "K2100095",
                 "C3100024",
"T1700056",
 "K2800066",
   "C3800071",
     "T1500050",
       "K2000083",
         "C2900044",
           "T1300022",
             "K1800009",
               "C4300074",
                 "T1600038",
"K3400005",
 "C4500091",
   "T3000049",
     "K1200077",
       "C2700080",
         "T2900062",
           "K1700093",
             "C4100036",
               "T2200077",
                 "K2400011",
"C3300048",
 "T1900009",
   "K3100055",
     "C3500022",
       "T2300019",
         "K3200083",
           "C3000067",
             "T2000072",
               "K2900011",
                 "C4200064",
"T2600090",
 "K3300050",
   "C3900012",
     "T2400081",
       "K3600075",
         "C3400029",
           "T1100042",
             "K1500034",
               "C4000051",
                 "T1800086",
"K2600008",
 "C3700061",
   "T2100065",
     "K1900057",
       "C2800033",
         "T3000024",
           "K2200081",
             "C4300062",
               "T1200047",
                 "K2800099",
"C3800050",
 "T2000034",
   "K3100078",
     "C2900009",
       "T1600023",
         "K1400088",
           "C4100073",
             "T2300058",
               "K3300019",
                 "C3500066",
"T2700046",
 "K1800057",
   "C3200013",
     "T1400032",
       "K2500091",
         "C3600040",
           "T2200074",
             "K1200053",
               "C4400085",
                 "T2500098"


])