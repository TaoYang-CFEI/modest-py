# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.
This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.
"""
import json
import os
import pandas as pd
from modestpy import Estimation
from modestpy.utilities.sysarch import get_sys_arch


if __name__ == "__main__":
    """
    This file is supposed to be run from the root directory.
    Otherwise the paths have to be corrected.
    """

    # DATA PREPARATION ==============================================
    # Resources
    platform = get_sys_arch()
    assert platform, 'Unsupported platform type!'
    fmu_file = 'Simple2R1C_ic_' + platform + '.fmu'

    fmu_path = os.path.join('examples', 'simple', 'resources', fmu_file)
    inp_path = os.path.join('examples', 'simple', 'resources', 'inputs.csv')
    ideal_path = os.path.join('examples', 'simple', 'resources', 'result.csv')
    est_path = os.path.join('examples', 'simple', 'resources', 'est.json')
    known_path = os.path.join('examples', 'simple', 'resources', 'known.json')

    rmse = list()
    for i in range(3):
        # Working directory
        workdir = os.path.join('examples', 'simple', 'workdir',
                               'simple-{}'.format(i))
        if not os.path.exists(workdir):
            os.makedirs(workdir)
            assert os.path.exists(workdir), "Work directory does not exist"

        # Load inputs
        inp = pd.read_csv(inp_path).set_index('time')

        # Load measurements (ideal results)
        ideal = pd.read_csv(ideal_path).set_index('time')

        # Load definition of estimated parameters (name, initial value, bounds)
        with open(est_path) as f:
            est = json.load(f)

        # Load definition of known parameters (name, value)
        with open(known_path) as f:
            known = json.load(f)

        # MODEL IDENTIFICATION ==========================================
        session = Estimation(workdir, fmu_path, inp, known, est, ideal,
                             lp_n=1, lp_len=50000, lp_frame=(0, 50000),
                             vp=(0, 50000), ic_param={'Tstart': 'T'},
                             methods=('GA_LEGACY', 'PS'),
                             ga_opts={'maxiter': 5, 'tol': 0.001, 'lhs': True},
                             ps_opts={'maxiter': 5, 'tol': 1e-6},
                             scipy_opts={},
                             ftype='RMSE', seed=1)

        estimates = session.estimate()
        err, res = session.validate()
        rmse.append(err['tot'])

    print('====================================================')
    print('Random seed works if you get the same results below:')
    for el in rmse:
        print(el)
