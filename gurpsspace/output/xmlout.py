"""latexout.py

Module for saving all the information about a StarSystem to a LaTeX file for
processing towards a nicely formatted PDF file.
"""

#from ..starsystem import StarSystem
from ..tables import AtmCompAbbr

class XmlWriter:
    def __init__(self, starsystem, filename='starsystem.xml'):
        self.starsystem = starsystem
        self.filename = filename

    def write(self):
        # Open the file
        file = open(self.filename, 'w')

        # Write the preamble
        file.write(self.preamble())

        # Write stellar system and star properties
        file.write(self.starsystemprop())

        # file.write(self.starprop())

        # Write the overviews
        # file.write(self.overviews())

        # Write the detailed planet system chapters
        # for star in self.starsystem.stars:
        #     str = self.psdetails(star.planetsystem)
        #     file.write(str)

        # Close the file
        file.close()

    def preamble(self):
        preambulum = """<?xml version="1.0" encoding="UTF-8"?>"""
        return preambulum

    def starsystemprop(self):
        str = "<starsystem>\n"
        
        numstar = len(self.starsystem.stars)
        str += "<starNumber>{}</starNumber>\n".format(numstar)
        
        age = self.starsystem.getAge()
        str += '<systemAge unit="billion years">{}</systemAge>\n'.format(age)

        # Only put table (about the properties of the stellar system) if
        # necessary (i.e. more than one star)
        if numstar > 1:
            # Extract orbit and eccentricities
            oecc = self.starsystem.getOrbits()
            for o, e in oecc:
                str += '<systemOrbitalSeparation unit="AU">{}</systemOrbitalSeparation>\n'.format(o)
                str += "<systemOrbitalEccentricity>{}</systemOrbitalEccentricity>\n".format(round(e))

            for per in self.starsystem.getPeriod():
                str += "<systemOrbitalPeriod>{}</systemOrbitalPeriod>\n".format(per)
        
        str += "<stars>\n"
        for star in self.starsystem.stars:
            str += self.starprop(star)
        str += "</stars>\n"
        
        str += "</starsystem>\n"
        return str

    def starprop(self, star):
        str = ""
        
        str += "<star>\n"
        str += "<sequence>" + star.getSequence() + "</sequence>\n"
        str += '<mass unit="Solar Mass">{}</mass>\n'.format(star.getMass())
        str += '<temperature unit="Kelvin">{}</temperature>\n'.format(star.getTemp())
        str += '<luminosity unit="Solar Luminosity">{}</luminosity>\n'.format(star.getLuminosity())
        str += '<radius unit="kilometer">{}</radius>\n'.format(star.getRadius() * 149597871)
        str += '<innerOrbitLimit unit="AU">{}</innerOrbitLimit>\n'.format(star.getOrbitlimits()[0])
        str += '<outerOrbitLimit unit="AU">{}</outerOrbitLimit>\n'.format(star.getOrbitlimits()[1])
        str += '<snowline unit="AU">{}</snowline>\n'.format(star.getSnowline())
        if star.hasForbidden():
            str += '<forbiddenZoneInner unit="AU">{}</forbiddenZoneInner>\n'.format(star.getForbidden()[0])
            str += '<forbiddenZoneOuter unit="AU">{}</forbiddenZoneOuter>\n'.format(star.getForbidden()[1])
            
        str += '<orbits>\n'
        orbits = star.planetsystem.getOrbitcontents()
        
        for key in orbits:
            orbit = orbits[key]
            str += '<orbit>\n'
            
#            str += '<number>{}</number>\n'.format(orbit.getNumber)
#            str += '<distance unit="AU">{}</orbit>\n'.format(orbit.getOrbit)
            str += '<type>{}</type>\n'.format(orbit.getType())
            
            type = orbits[key].type()
            if type == 'Terrestrial':
                str += '<planet>Terrestrial</planet>\n'
                # str += self.planetdetails(orbit)
            if type == 'Gas Giant':
                str += '<planet>Gas Giant</planet>\n'
        str += '</orbits>\n'
        
        str += "</star>\n"
        return str

    def psdetails(self, planetsystem):
        """Print details about the planet system

        Every new section is a new orbiting object, be it terrestrial planet,
        gas giant or major moon
        """
        letter = planetsystem.parentstar.getLetter()
        oc = planetsystem.getOrbitcontents()
        str = '\chapter{Planet System ' + letter + '}\n\n'
        # Call for each celestial body the function to print its details
        for key in sorted(oc):
            type = oc[key].type()
            if type == 'Terrestrial':
                str += self.planetdetails(oc[key])
            if type == 'Gas Giant':
                str += self.gasgiantdetails(oc[key])
        return str

    def planetdetails(self, planet):
        str = ''
        str += '<name>{}</name>\n'.format(planet.getName())
        str += '<type>{} {}</type>\n'.format(planet.getSize(), planet.getType())
        
        atcomp = planet.atmcomp
        atkeys = [key for key in planet.atmcomp.keys() if planet.atmcomp[key] == True]
        abbr = ''
        for k in atkeys:
            abbr += AtmCompAbbr[k] + ', '
        if len(atkeys) > 0:
            str += 'Atm. Comp. & {} \\\\ \n'.format(abbr[:-2])
        if planet.getPressure() == 0:
            str += 'Pressure & None \\\\ \n'
        else:
            str += 'Pressure & {:.2f} atm, {} \\\\ \n'.format(planet.getPressure(), planet.getPressCat())
        
        str += '<hydrographicCoverage>{}\%\n</hydrographicCoverage>'.format(planet.getHydrocover())
        str += 'Average $T_\mathrm{surf}$ & {temp:.1f} K \\\\ \n'.format(surf='{surf}',temp=planet.getAvSurf())
        str += 'Climate Type & {} \\\\ \n'.format(planet.getClimate())
        str += 'Diameter & {:.3f} Earth Diameters\\\\ \n'.format(planet.getDiameter())
        str += 'Surface Gravity & {:.2f} G \\\\ \n'.format(planet.getGravity())
        str += 'Affinity & {:+.0f} \\\\ \n'.format(planet.getAffinity())
        if planet.numMoons() > 0:
            str += 'Moons & {} \\\\ \n'.format(planet.numMoons())
        if planet.numMoonlets() > 0:
            str += 'Moonlets & {} \\\\ \n'.format(planet.numMoonlets())
        str += '\\bottomrule\n\end{tabular}\n\end{table}\n\\vfill\n\n'
        str += '%\subsection{Social Parameters}\n'
        str += '%\subsection{Installations}\n\n'

        if planet.numMoons() > 0:
            moons = planet.getSatellites()
            for m in moons:
                str += self.moondetails(m)
        return str

    def gasgiantdetails(self, gasgiant):
        """Print details about gas giants"""
        str = '\section{Gas Giant ' + gasgiant.getName() + '}\n'
        str += '\subsection{Summary}\n'
        str += '\subsection{World Properties}\n'
        str += '\\begin{table}[H]\n\centering\n'
        str += '\\begin{tabular}{ll}\n'
        str += '\\toprule\n'
        str += 'Property & Value \\\\ \n'
        str += '\midrule\n'
        str += 'Mass & {} Earth Masses\\\\ \n'.format(gasgiant.getMass())
        str += 'Density & {} Earth Densities \\\\ \n'.format(gasgiant.getDensity())
        str += 'Diameter & {:.2f} Earth Diameters \\\\ \n'.format(gasgiant.getDiameter())
        str += 'Cloud-Top Gravity & {:.2f} G \\\\ \n'.format(gasgiant.getGravity())
        str += 'Satellites $1^\mathrm{st}$ Family & {num} \\\\ \n'.format(st='{st}', num=len(gasgiant.getFirstFamily()))
        str += 'Satellites $2^\mathrm{nd}$ Family & {num} \\\\ \n'.format(nd='{nd}', num=len(gasgiant.getMoons()))
        str += 'Satellites $3^\mathrm{rd}$ Family & {num} \\\\ \n'.format(rd='{rd}', num=len(gasgiant.getThirdFamily()))
        str += '\\bottomrule\n'
        str += '\end{tabular}\n\end{table}\n\\vfill\n\n'

        moons = gasgiant.getMoons()
        for m in moons:
            str += self.moondetails(m)
        return str

    def moondetails(self, moon):
        """Print details about a major moon"""
        str = '\section{Moon ' + moon.getName() + '}\n'
        str += '%\subsection{Summary}\n\n'
        str += '\subsection{World Properties}\n'
        str += '\\begin{table}[H]\n\centering\n'
        str += '\\begin{tabular}{ll}\n'
        str += '\\toprule\n'
        str += 'Property & Value \\\\ \n\midrule\n'
        str += 'Type & {} ({})\\\\ \n'.format(moon.getSize(), moon.getType())
        atcomp = moon.atmcomp
        atkeys = [key for key in moon.atmcomp.keys() if moon.atmcomp[key] == True]
        abbr = ''
        for k in atkeys:
            abbr += AtmCompAbbr[k] + ', '
        if len(atkeys) > 0:
            str += 'Atm. Comp. & {} \\\\ \n'.format(abbr[:-2])
        if moon.getPressure() == 0:
            str += 'Pressure & None \\\\ \n'
        else:
            str += 'Pressure & {:.2f} atm, {} \\\\ \n'.format(moon.getPressure(), moon.getPressCat())
        str += 'Hydrographic Coverage & {:.0f} \% \\\\ \n'.format(moon.getHydrocover())
        str += 'Average $T_\mathrm{surf}$ & {temp:.1f} K \\\\ \n'.format(surf='{surf}',temp=moon.getAvSurf())
        str += 'Climate Type & {} \\\\ \n'.format(moon.getClimate())
        str += 'Diameter & {:.3f} Earth Diameters\\\\ \n'.format(moon.getDiameter())
        str += 'Surface Gravity & {:.2f} G \\\\ \n'.format(moon.getGravity())
        str += 'Affinity & {:+.0f} \\\\ \n'.format(moon.getAffinity())
        str += '\\bottomrule\n\end{tabular}\n\end{table}\n\\vfill\n\n'
        str += '%\subsection{Social Parameters}\n'
        str += '%\subsection{Installations}\n\n'
        return str
