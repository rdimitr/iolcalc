import math
import csv

A = 0
ACD = 0
SF = 0

na=1.336
nc=1.333
V=12

VarsDictionary = []

    
def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def getPowerIOL(a_const, eye_length, plan_refr, meridian1, meridian2):
    pwiol = [0,0,0,0,0,0,0]
    eL = 0.0
    K1 = 0.0
    K2 = 0.0
    REF = 0.0
    
    global A
    global ACD
    global SF
    
    VarsDictionary.clear()
    
    with open('.\data\AconstDot.csv') as f:
         reader = csv.reader(f, delimiter=':')
         for row in reader:
             VarsDictionary.append((row[0],row[1], row[2]))
             
    for i in range(len(VarsDictionary)):
        if VarsDictionary[i][0] == a_const:
           A = float(a_const)
           ACD = float(VarsDictionary[i][1])
           SF = float(VarsDictionary[i][2])
    
    eL = float(eye_length)
    K1 = float(meridian1)
    K2 = float(meridian2)
    REF= float(plan_refr)
             
    pwiol[0] = SRK_2(eL, K1, K2, REF)
    pwiol[1] = SRK_T(eL, K1, K2, REF)
    pwiol[2] = Holaday(eL, K1, K2, REF)
    pwiol[3] = Haigis(eL, K1, K2, REF)
    pwiol[4] = HofferQ(eL, K1, K2, REF)
    pwiol[5] = Shammas(eL, K1, K2, REF)
    pwiol[6] = Fedorov(eL, K1, K2)

    return pwiol	
    
    

def SRK_2(eye_length, meridian1, meridian2, refr):
     if eye_length < 20:
        A1 = A + 3
     if (eye_length >= 20) and (eye_length < 21):
        A1 = A + 2
     if (eye_length >= 21) and (eye_length < 22):
        A1 = A + 1
     if (eye_length >= 22) and (eye_length < 24.5):
        A1 = A
     if eye_length >= 24.5:
        A1 = A - 0.5

     K = (meridian1 + meridian2)/2

     P_emme=A1 - 0.9*K -2.5*eye_length-0

     if P_emme < 14:
        CR = 1.00
     if P_emme >= 14:
        CR = 1.25

     P_ametr=P_emme - CR*refr

     return P_ametr
	
    
def SRK_T(eye_length, meridian1, meridian2, refr):
    K = (meridian1 + meridian2)/2
    r=337.5/K
    Ofst=(0.62467*A - 68.747) - 3.336
    
    if eye_length <  24.2:
       LC=eye_length
    else:
       LC=-3.446 + 1.716*eye_length - 0.0237*eye_length*eye_length

    W=-5.41 + 0.58412*LC + 0.098*K
    H=r - math.sqrt(r*r - (W*W/4) )
    C1=H + Ofst
    L1=eye_length + (0.65696 - 0.02029*eye_length)
    X=na*r - L1*(nc-1)
    Y=na*r - C1*(nc-1)
    P_ametr=(1000*na*(X-0.001*refr*(V*X + L1*r))) / ( (L1-C1)*(Y-0.001*refr*(V*Y+C1*r)) )

    return P_ametr
    
    
	
def Holaday(eye_length, meridian1, meridian2, refr):
    K = (meridian1 + meridian2)/2
    r=337.5/K
    L2= eye_length + 0.2

    if r<=7:
       Rag=7
    else:
       Rag=r

    AG=12.5*eye_length/23.45
    if AG > 13.5:
       AG=13.5

    C2=0.56 + Rag - math.sqrt( (Rag*Rag) - ((AG*AG)/4) )
    X=na*r - L2*(nc-1)
    Y=na*r - (nc-1)*(C2+SF)
    P_ametr=( 1000*na*(X - 0.001*refr*(V*X + L2*r)) )/( (L2-C2-SF)*(Y - 0.001*refr*(V*Y + r*(C2+SF))) )

    return P_ametr
    
	
def Haigis(eye_length, meridian1, meridian2, refr):
     K = (meridian1 + meridian2)/2
     RC =337.5 /K
     DC=1000*(nc-1)/RC
     z = DC + (refr/(1-(refr*V/1000)))
     P_ametr = ( (1000*na)/(eye_length-ACD) ) - (na/( (na/z) - (ACD/1000)) )

     return P_ametr
    
    

def HofferQ(eye_length, meridian1, meridian2, refr):
     K = (meridian1 + meridian2)/2
     P_ametr= (1336/(eye_length-ACD-0.05)) - (1.336/( (1.336/(K+refr))-((ACD+0.05)/1000) ))
     
     return P_ametr
	
 
def Shammas(eye_length, meridian1, meridian2, refr):
     K = (meridian1 + meridian2)/2
     P_ametr1 = (1336/(eye_length-0.1*(eye_length-23)-ACD-0.05))
     P_ametr2 = (1/((1.0125/K)-((ACD+0.05)/1336)))
     P_ametr = P_ametr1 - P_ametr2

     return P_ametr


def Fedorov(eye_length, meridian1, meridian2):
    AL = eye_length*0.001
    K = (meridian1 + meridian2)/2
    P_emmetr = ( 1.336 - (K*AL) )/( (AL-0.003)*(1-(K*(0.003/1.336))) ) + 3

    return P_emmetr