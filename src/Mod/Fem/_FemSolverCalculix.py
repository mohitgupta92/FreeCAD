# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - Bernd Hahnebach <bernd@bimstatik.org>            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "_FemSolverCalculix"
__author__ = "Bernd Hahnebach"
__url__ = "http://www.freecadweb.org"


import FreeCAD
import FemToolsCcx


class _FemSolverCalculix():
    """The Fem::FemSolver's Proxy python type, add solver specific properties
    """
    def __init__(self, obj):
        self.Type = "FemSolverCalculix"
        self.Object = obj  # keep a ref to the DocObj for nonGui usage
        obj.Proxy = self  # link between App::DocumentObject to  this object

        obj.addProperty("App::PropertyString", "SolverType", "Base", "Type of the solver", 1)  # the 1 set the property to ReadOnly
        obj.SolverType = str(self.Type)

        fem_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fem/General")
        ccx_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fem/Ccx")

        obj.addProperty("App::PropertyPath", "WorkingDir", "Fem", "Working directory for calculations")
        obj.WorkingDir = fem_prefs.GetString("WorkingDir", "")

        obj.addProperty("App::PropertyEnumeration", "AnalysisType", "Fem", "Type of the analysis")
        obj.AnalysisType = FemToolsCcx.FemToolsCcx.known_analysis_types
        analysis_type = ccx_prefs.GetInt("AnalysisType", 0)
        obj.AnalysisType = FemToolsCcx.FemToolsCcx.known_analysis_types[analysis_type]

        known_geom_nonlinear_types = ["linear", "nonlinear"]
        obj.addProperty("App::PropertyEnumeration", "GeometricalNonlinearity", "Fem", "Type of geometrical nonlinearity")
        obj.GeometricalNonlinearity = known_geom_nonlinear_types
        geom = ccx_prefs.GetBool("NonlinearGeometry", False)
        if geom is True:
            obj.GeometricalNonlinearity = known_geom_nonlinear_types[1]  # nonlinear
        else:
            obj.GeometricalNonlinearity = known_geom_nonlinear_types[0]  # linear

        obj.addProperty("App::PropertyIntegerConstraint", "EigenmodesCount", "Fem", "Number of modes for frequency calculations")
        noe = ccx_prefs.GetInt("EigenmodesCount", 10)
        obj.EigenmodesCount = (noe, 1, 100, 1)

        obj.addProperty("App::PropertyFloatConstraint", "EigenmodeLowLimit", "Fem", "Low frequency limit for eigenmode calculations")
        ell = ccx_prefs.GetFloat("EigenmodeLowLimit", 0.0)
        obj.EigenmodeLowLimit = (ell, 0.0, 1000000.0, 10000.0)

        obj.addProperty("App::PropertyFloatConstraint", "EigenmodeHighLimit", "Fem", "High frequency limit for eigenmode calculations")
        ehl = ccx_prefs.GetFloat("EigenmodeHighLimit", 1000000.0)
        obj.EigenmodeHighLimit = (ehl, 0.0, 1000000.0, 10000.0)

        obj.addProperty("App::PropertyIntegerConstraint", "IterationsMaximum", "Fem", "Number of iterations allowed before stopping jobs")
        niter = ccx_prefs.GetInt("AnalysisMaxIterations", 200)
        obj.IterationsMaximum = niter

        obj.addProperty("App::PropertyFloatConstraint", "TimeInitialStep", "Fem", "Initial time steps")
        ini = ccx_prefs.GetFloat("AnalysisTimeInitialStep", 1.0)
        obj.TimeInitialStep = ini

        obj.addProperty("App::PropertyFloatConstraint", "TimeEnd", "Fem", "End time analysis")
        eni = ccx_prefs.GetFloat("AnalysisTime", 1.0)
        obj.TimeEnd = eni

        obj.addProperty("App::PropertyBool", "SteadyState", "Fem", "Run steady state or transient analysis")
        sted = ccx_prefs.GetBool("StaticAnalysis", True)
        obj.SteadyState = sted

        obj.addProperty("App::PropertyBool", "IterationsControlParameterTimeUse", "Fem", "Use the user defined time incrementation control parameter")
        use_non_ccx_iterations_param = ccx_prefs.GetInt("UseNonCcxIterationParam", False)
        obj.IterationsControlParameterTimeUse = use_non_ccx_iterations_param

        ccx_default_time_incrementation_control_parameter = {
            # iteration parameter
            'I_0': 4,
            'I_R': 8,
            'I_P': 9,
            'I_C': 200,  # ccx default = 16
            'I_L': 10,
            'I_G': 400,  # ccx default = 4
            'I_S': None,
            'I_A': 200,  # ccx default = 5
            'I_J': None,
            'I_T': None,
            # cutback parameter
            'D_f': 0.25,
            'D_C': 0.5,
            'D_B': 0.75,
            'D_A': 0.85,
            'D_S': None,
            'D_H': None,
            'D_D': 1.5,
            'W_G': None}
        p = ccx_default_time_incrementation_control_parameter
        p_iter = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}'.format(p['I_0'], p['I_R'], p['I_P'], p['I_C'], p['I_L'], p['I_G'], '', p['I_A'], '', '')
        p_cutb = '{0},{1},{2},{3},{4},{5},{6},{7}'.format(p['D_f'], p['D_C'], p['D_B'], p['D_A'], '', '', p['D_D'], '')
        obj.addProperty("App::PropertyString", "IterationsControlParameterIter", "Fem", "User defined time incrementation iterations control parameter")
        obj.IterationsControlParameterIter = p_iter
        obj.addProperty("App::PropertyString", "IterationsControlParameterCutb", "Fem", "User defined time incrementation cutbacks control parameter")
        obj.IterationsControlParameterCutb = p_cutb

        known_ccx_solver_types = ["default", "spooles", "iterativescaling", "iterativecholesky"]
        obj.addProperty("App::PropertyEnumeration", "MatrixSolverType", "Fem", "Type of solver to use")
        obj.MatrixSolverType = known_ccx_solver_types
        solver_type = ccx_prefs.GetInt("Solver", 0)
        obj.MatrixSolverType = known_ccx_solver_types[solver_type]

    def execute(self, obj):
        return

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
