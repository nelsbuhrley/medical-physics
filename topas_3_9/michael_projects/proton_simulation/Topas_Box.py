# Topas_Box.py
# Generates a TOPAS parameter file for a proton beam hitting a spherical tumor

class Proton_Beam:

    def make_box():
        return """
# ============================================================
# WORLD GEOMETRY
# ============================================================

s:Ge/World/Type = "TsBox"
d:Ge/World/HLX = 20 cm
d:Ge/World/HLY = 20 cm
d:Ge/World/HLZ = 20 cm
s:Ge/World/Material = "G4_AIR"

# ============================================================
# WATER BOX (Patient Phantom)
# ============================================================

s:Ge/MyBox/Type = "TsBox"
s:Ge/MyBox/Material = "G4_WATER"
s:Ge/MyBox/Parent = "World"

d:Ge/MyBox/HLX = 10 cm
d:Ge/MyBox/HLY = 10 cm
d:Ge/MyBox/HLZ = 10 cm

d:Ge/MyBox/TransX = 0 cm
d:Ge/MyBox/TransY = 0 cm
d:Ge/MyBox/TransZ = 0 cm

# Physics
sv:Ph/Default/Modules = 1 "g4em-standard_opt0"

# Visualization
s:Gr/ViewA/Type = "OpenGL"
i:Gr/ViewA/WindowSizeX = 1024
i:Gr/ViewA/WindowSizeY = 768
b:Gr/ViewA/IncludeAxes = "False"

d:Gr/ViewA/Theta = 55 deg
d:Gr/ViewA/Phi = 20 deg

s:Gr/ViewA/Projection = "Perspective"
d:Gr/ViewA/PerspectiveAngle = 45 deg

u:Gr/ViewA/Zoom = 15.

b:Ts/PauseBeforeQuit = "True"
"""

    def make_tumor():
        return """
# ============================================================
# SPHERICAL TUMOR
# ============================================================

s:Ge/Tumor/Parent = "MyBox"
s:Ge/Tumor/Type = "TsSphere"
s:Ge/Tumor/Color = "red"

s:Ge/Tumor/Material = "G4_TISSUE_SOFT_ICRP"

d:Ge/Tumor/RMax = 2 cm
d:Ge/Tumor/RMin = 0 cm

d:Ge/Tumor/TransX = 0 cm
d:Ge/Tumor/TransY = 0 cm
d:Ge/Tumor/TransZ = 5 cm

i:Ge/Tumor/XBins = 40
i:Ge/Tumor/YBins = 40
i:Ge/Tumor/ZBins = 40


"""

    def make_beam():
        return """
# ============================================================
# PROTON BEAM SOURCE
# ============================================================

s:So/ProtonBeam/Component = "World"
s:So/ProtonBeam/Type = "Beam"

s:So/ProtonBeam/BeamParticle = "proton"
d:So/ProtonBeam/BeamEnergy = 67.5 MeV

i:So/ProtonBeam/NumberOfHistoriesInRun = 10000

s:So/ProtonBeam/BeamPositionDistribution = "None"
d:So/ProtonBeam/BeamPositionX = 0 cm
d:So/ProtonBeam/BeamPositionY = 0 cm
d:So/ProtonBeam/BeamPositionZ = -15 cm

s:So/ProtonBeam/BeamAngularDistribution = "None"
"""

    def dose_score():
        return """
# ============================================================
# DOSE SCORING
# ============================================================

s:Sc/Dose/IfOutputFileAlreadyExists = "Overwrite"
s:Sc/Dose/Quantity = "DoseToMedium"
s:Sc/Dose/Component = "Tumor"
s:Sc/Dose/OutputFileName = "dose"
"""

    def dose_grid():
        return """
# ============================================================
# 3D DOSE GRID FOR PARAVIEW
# ============================================================

# Dose scoring

s:Sc/Dose3D/Quantity = "DoseToMedium"
s:Sc/Dose3D/Component = "Tumor"

i:Sc/Dose3D/NumberOfBinsX = 50
i:Sc/Dose3D/NumberOfBinsY = 50
i:Sc/Dose3D/NumberOfBinsZ = 50

s:Sc/Dose3D/OutputType = "CSV"
s:Sc/Dose3D/OutputFile = "dose3d"
s:Sc/Dose3D/IfOutputFileAlreadyExists = "Increment"

"""

# ============================================================
# Combine all sections into one TOPAS file
# ============================================================

def run_simulation():
    return (
        Proton_Beam.make_box() +
        Proton_Beam.make_tumor() +
        Proton_Beam.make_beam() +
        Proton_Beam.dose_score() +
	Proton_Beam.dose_grid()
    )


# ============================================================
# Write the TOPAS parameter file
# ============================================================

with open("testbox.txt", "w") as f:
    f.write(run_simulation())

print("TOPAS parameter file 'testbox.txt' generated successfully.")
