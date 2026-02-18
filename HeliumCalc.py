from ambiance import Atmosphere
#Inputs

#Masses
Mpayload = 38*10**-3 #kg
Mballoon = 47*10**-3 #kg
targetAltitude = 11090 #Meters
launchAltitude = 0 #Meters
HeliumPurity = 0.99
NumBalloons = 1
#VBalt = NumBalloons*0.03514469026222474004 #m3 for a balloon 16" dia
#VBalt = NumBalloons*0.09136246628715064257 #m3 for a balloon 22" dia
#VBalt = NumBalloons*1.075 #m3 for a balloon 50" dia
VBalt = 0.281156*NumBalloons #m3 for a 32" balloon
Mballoon = NumBalloons*Mballoon
#densityof mylar ~24g/m^2

#Constants
molWeightHelium = 4.002602*10**-3 #kg/mol
molWeightAir = 28.013*10**-3 #kg/mol
molWeightHelium = molWeightHelium*HeliumPurity+(1-HeliumPurity)*molWeightAir #adjusts molweight helium
atmoAtAlt = Atmosphere(targetAltitude)
atmoAtGnd = Atmosphere(launchAltitude)
R = 8.314472 #ideal gas constant

#Math
Palt = ((atmoAtAlt.density*VBalt-Mballoon-Mpayload)*R*atmoAtAlt.temperature)/(VBalt*molWeightHelium)
print("Pressure at alt-ambiant air pressure [Pa]:",Palt-atmoAtAlt.pressure)

n = (Palt*VBalt)/(R*atmoAtAlt.temperature)
print("Mols of helium needed [Mols]",n)

Vgnd = n*R*atmoAtGnd.temperature/atmoAtGnd.pressure
print("Volume of balloon at ground:",Vgnd)

FreeLift = atmoAtGnd.density*Vgnd-(n*molWeightHelium) - Mballoon-Mpayload
print("Freelift [g]:",FreeLift*10**3)
print("Freelift per balloon [g]:",FreeLift*10**3/NumBalloons)
print("LIFT PER BALLOON [g]:",((FreeLift+Mpayload)*10**3)/NumBalloons)