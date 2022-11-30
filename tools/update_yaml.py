#!/usr/bin/env python3

import argparse
import datetime
import os
import yaml
import numpy as np

# Correct date formatting
def correct_date(d):
    if isinstance(d, dict):
        # Loop over dictionary items
        for k,v in d.items():
            d[k] = correct_date(v)
    elif isinstance(d, list):
        # Loop over list items
        i = 0
        for v in d:
            d[i] = correct_date(v)
            i += 1

    if isinstance(d, datetime.datetime):
        # Replace with string
        d = d.strftime("%Y-%m-%dT%H:%M:%SZ")
    return d

# Find bump subsections and their indentation
def find_bump(d, bumps):
    if isinstance(d, dict):
        # Loop over dictionary items
        for k,v in d.items():
            # Check for bump subsection
            if k == "bump":
                bumps.append(v)
            else:
                find_bump(v, bumps)
    elif isinstance(d, list):
        # Loop over list items
        for v in d:
            find_bump(v, bumps)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("filename", help="Yaml file name")
parser.add_argument('--variables', nargs='+', help='Variables', default=['var1','var2','var3','var4'])
args = parser.parse_args()
print("File: " + args.filename)

# Read yaml file
with open(args.filename, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Correct date formatting recursively
correct_date(config)

# Look for bump sections
bumps = []
find_bump(config, bumps)

# BUMP structure
kv = []

general = {}
general["name"] = "general"
general["keys"] = ["testing"]
kv.append(general)

io = {}
io["name"] = "io"
io["keys"] = []
kv.append(io)

drivers = {}
drivers["name"] = "drivers"
drivers["keys"] = []
kv.append(drivers)

model = {}
model["name"] = "model"
model["keys"] = ["nl0", "levs", "lev2d", "variables"]
kv.append(model)

ensembleSizes = {}
ensembleSizes["name"] = "ensemble sizes"
ensembleSizes["keys"] = ["ens1_ne", "ens1_nsub", "ens2_ne", "ens2_nsub"]
kv.append(ensembleSizes)

mask = {}
mask["name"] = "mask"
mask["keys"] = ["mask_type", "mask_lu", "mask_th", "ncontig_th", "mask_check"]
kv.append(mask)

sampling = {}
sampling["name"] = "sampling"
sampling["keys"] = ["nc1", "nc2", "nc3", "nc4", "dc", "nl0r", "local_diag", "local_rad", "local_dlat", "irmax"]
kv.append(sampling)

localization = {}
localization["name"] = "localization"
localization["keys"] = ["ne", "ne_lr", "gau_approx", "gen_kurt_th", "avg_nbins"]
kv.append(localization)

verticalBalance = {}
verticalBalance["name"] = "vertical balance"
verticalBalance["keys"] = ["vbal_rad", "vbal_dlat", "vbal_pseudo_inv", "vbal_pseudo_inv_mmax", "vbal_pseudo_inv_var_th", "vbal_id"]
kv.append(verticalBalance)

variance = {}
variance["name"] = "variance"
variance["keys"] = ["forced_var", "var_filter", "var_niter", "var_npass"]
kv.append(variance)

optimalityTest = {}
optimalityTest["name"] = "optimality test"
optimalityTest["keys"] = ["optimality_nfac", "optimality_delta", "optimality_ntest"]
kv.append(optimalityTest)

fit = {}
fit["name"] = "fit"
fit["keys"] = ["diag_rhflt", "diag_rvflt", "fit_dl0", "fit_ncmp"]
kv.append(fit)

localProfiles = {}
localProfiles["name"] = "local profiles"
localProfiles["keys"] = ["nldwv", "lon_ldwv", "lat_ldwv", "name_ldwv"]
kv.append(localProfiles)

nicas = {}
nicas["name"] = "nicas"
nicas["keys"] = ["resol", "nc1max", "nicas_draw_type", "forced_radii", "pos_def_test", "interp_test"]
kv.append(nicas)

wind = {}
wind["name"] = "wind"
wind["keys"] = ["wind_streamfunction", "wind_velocity_potential", "wind_zonal", "wind_meridional", "wind_nlon", "wind_nlat", "wind_nsg", "wind_inflation"]
kv.append(wind)

sections = ["general", "io", "drivers", "model", "sampling", "localization", "vertical balance", "variance", "optimality test", "fit", "local profiles", "nicas", "wind"]
other_sections = ["ensemble", "lowres ensemble", "operators application"]

# Upgrade bump sections
for i in range(len(bumps)):
    # Prepare new_bump
    new_bump = {}
    for section in sections:
        new_bump[section] = {}

    # Copy existing keys
    old_bump = bumps[i]
    for j in range(len(kv)):
        section = {}
        for item in kv[j]["keys"]:
            if item in old_bump:
                section[item] = old_bump[item]
        if section:
            new_bump[kv[j]["name"]] = section

    # Copy existing keys in grids
    if "grids" in old_bump:
        old_grids = old_bump["grids"]
        new_grids = []
        for old_grid in old_grids:
            new_grid = {}
            for j in range(len(kv)):
                section = {}
                for item in kv[j]["keys"]:
                    if item in old_grid:
                        section[item] = old_grid[item]
                if section:
                    new_grid[kv[j]["name"]] = section

            # Append grid
            new_grids.append(new_grid)

        # Reset grid
        new_bump["grids"] = new_grids

    # Update general section
    if "colorlog" in old_bump:
        new_bump["general"]["color log"] = old_bump["colorlog"]
    if "default_seed" in old_bump:
        new_bump["general"]["default seed"] = old_bump["default_seed"]
    if "repro" in old_bump:
        new_bump["general"]["reproducibility operators"] = old_bump["repro"]
    if "rth" in old_bump:
        new_bump["general"]["reproducibility threshold"] = old_bump["rth"]
    if "universe_rad" in old_bump:
        new_bump["general"]["universe radius"] = old_bump["universe_rad"]

    # Update io section
    if "datadir" in old_bump:
        new_bump["io"]["data directory"] = old_bump["datadir"]
    if "prefix" in old_bump:
        new_bump["io"]["files prefix"] = old_bump["prefix"]
    if "parallel_io" in old_bump:
        new_bump["io"]["parallel netcdf"] = old_bump["parallel_io"]
    if "nprocio" in old_bump:
        new_bump["io"]["io task number"] = old_bump["nprocio"]
    if "fname_samp" in old_bump:
        new_bump["io"]["overriding sampling file"] = old_bump["fname_samp"]
    if "fname_vbal_cov" in old_bump:
        new_bump["io"]["overriding vertical covariance file"] = old_bump["fname_vbal_cov"]
    if "fname_vbal" in old_bump:
        new_bump["io"]["overriding vertical balance file"] = old_bump["fname_vbal"]
    if "fname_mom" in old_bump:
        new_bump["io"]["overriding moments file"] = old_bump["fname_mom"]
    if "fname_nicas" in old_bump:
        new_bump["io"]["overriding nicas file"] = old_bump["fname_nicas"]
    if "fname_wind" in old_bump:
        new_bump["io"]["overriding psichitouv file"] = old_bump["fname_wind"]
    if "io_keys" in old_bump:
        vec = []
        for i in range(len(old_bump["io_keys"])):
            item = {}
            item["in code"] = old_bump["io_keys"][i]
            item["in file"] = old_bump["io_values"][i]
            vec.append(item)
        new_bump["io"]["alias"] = vec

    # Update drivers section
    if "method" in old_bump and "new_hdiag" in old_bump:
        if old_bump["method"] == "cor":
            new_bump["drivers"]["compute covariance"] = True
            new_bump["drivers"]["compute correlation"] = True
        if old_bump["method"] == "loc":
            new_bump["drivers"]["compute covariance"] = True
            new_bump["drivers"]["compute correlation"] = True
            new_bump["drivers"]["compute localization"] = True
        if old_bump["method"] == "hyb-rnd":
            new_bump["drivers"]["compute covariance"] = True
            new_bump["drivers"]["compute lowres covariance"] = True
            new_bump["drivers"]["compute correlation"] = True
            new_bump["drivers"]["compute lowres correlation"] = True
            new_bump["drivers"]["compute localization"] = True
            new_bump["drivers"]["compute hybrid weights"] = True
            new_bump["drivers"]["hybrid source"] = "randomized static"
        if old_bump["method"] == "hyb-ens":
            new_bump["drivers"]["compute covariance"] = True
            new_bump["drivers"]["compute lowres covariance"] = True
            new_bump["drivers"]["compute correlation"] = True
            new_bump["drivers"]["compute lowres correlation"] = True
            new_bump["drivers"]["compute localization"] = True
            new_bump["drivers"]["compute lowres localization"] = True
            new_bump["drivers"]["compute hybrid weights"] = True
            new_bump["drivers"]["hybrid source"] = "lowres ensemble"
    if "strategy" in old_bump:
        new_bump["drivers"]["multivariate strategy"] = old_bump["strategy"]
    if "new_normality" in old_bump:
        new_bump["drivers"]["compute normality"] = old_bump["new_normality"]
    if "load_samp_local" in old_bump:
        new_bump["drivers"]["load local sampling"] = old_bump["load_samp_local"]
    if "load_samp_global" in old_bump:
        new_bump["drivers"]["load global sampling"] = old_bump["load_samp_global"]
    if "write_samp_local" in old_bump:
        new_bump["drivers"]["write local sampling"] = old_bump["write_samp_local"]
    if "write_samp_global" in old_bump:
        new_bump["drivers"]["write global sampling"] = old_bump["write_samp_global"]
    if "" in old_bump:
        new_bump["drivers"]["write sampling grids"] = old_bump["write_samp_grids"]
    if "new_vbal_cov" in old_bump:
        new_bump["drivers"]["compute vertical covariance"] = old_bump["new_vbal_cov"]
    if "update_vbal_cov" in old_bump:
        new_bump["drivers"]["compute vertical covariance"] = old_bump["update_vbal_cov"]
        new_bump["drivers"]["iterative algorithm"] = old_bump["update_vbal_cov"]
    if "load_vbal_cov" in old_bump:
        new_bump["drivers"]["load vertical covariance"] = old_bump["load_vbal_cov"]
    if "write_vbal_cov" in old_bump:
        new_bump["drivers"]["write vertical covariance"] = old_bump["write_vbal_cov"]
    if "new_vbal" in old_bump:
        new_bump["drivers"]["compute vertical balance"] = old_bump["new_vbal"]
    if "load_vbal" in old_bump:
        new_bump["drivers"]["load vertical balance"] = old_bump["load_vbal"]
    if "write_vbal" in old_bump:
        new_bump["drivers"]["write vertical balance"] = old_bump["write_vbal"]
    if "new_var" in old_bump:
        new_bump["drivers"]["compute variance"] = old_bump["new_var"]
    if "update_var" in old_bump:
        new_bump["drivers"]["compute variance"] = old_bump["update_var"]
        new_bump["drivers"]["iterative algorithm"] = old_bump["update_var"]
    if "new_mom" in old_bump:
        new_bump["drivers"]["compute moments"] = old_bump["new_mom"]
    if "update_mom" in old_bump:
        new_bump["drivers"]["compute moments"] = old_bump["update_mom"]
        new_bump["drivers"]["iterative algorithm"] = old_bump["update_mom"]
    if "load_mom" in old_bump:
        new_bump["drivers"]["load moments"] = old_bump["load_mom"]
    if "write_mom" in old_bump:
        new_bump["drivers"]["write moments"] = old_bump["write_mom"]
    if "new_hdiag" in old_bump and not ("update_mom" in old_bump or "load_mom" in old_bump):
        new_bump["drivers"]["compute moments"] = True
    if "write_hdiag" in old_bump:
        new_bump["drivers"]["write diagnostics"] = old_bump["write_hdiag"]
    if "write_hdiag_detail" in old_bump:
        new_bump["drivers"]["write diagnostics detail"] = old_bump["write_hdiag_detail"]
    if "new_nicas" in old_bump:
        new_bump["drivers"]["compute nicas"] = old_bump["new_nicas"]
    if "load_nicas_local" in old_bump:
        new_bump["drivers"]["load local nicas"] = old_bump["load_nicas_local"]
    if "load_nicas_global" in old_bump:
        new_bump["drivers"]["load global nicas"] = old_bump["load_nicas_global"]
    if "write_nicas_local" in old_bump:
        new_bump["drivers"]["write local nicas"] = old_bump["write_nicas_local"]
    if "write_nicas_global" in old_bump:
        new_bump["drivers"]["write global nicas"] = old_bump["write_nicas_global"]
    if "write_nicas_grids" in old_bump:
        new_bump["drivers"]["write nicas grids"] = old_bump["write_nicas_grids"]
    if "new_wind" in old_bump:
        new_bump["drivers"]["compute psichitouv"] = old_bump["new_wind"]
    if "load_wind_local" in old_bump:
        new_bump["drivers"]["load local psichitouv"] = old_bump["load_wind_local"]
    if "write_wind_local" in old_bump:
        new_bump["drivers"]["write local psichitouv"] = old_bump["write_wind_local"]
    if "check_vbal" in old_bump:
        new_bump["drivers"]["vertical balance inverse test"] = old_bump["check_vbal"]
    if "check_adjoints" in old_bump:
        new_bump["drivers"]["adjoints test"] = old_bump["check_adjoints"]
    if "check_normalization" in old_bump:
        new_bump["drivers"]["normalization test"] = old_bump["check_normalization"]
    if "check_dirac" in old_bump:
        new_bump["drivers"]["internal dirac test"] = old_bump["check_dirac"]
    if "check_randomization" in old_bump:
        new_bump["drivers"]["randomization test"] = old_bump["check_randomization"]
    if "check_consistency" in old_bump:
        new_bump["drivers"]["internal consistency test"] = old_bump["check_consistency"]
    if "check_optimality" in old_bump:
        new_bump["drivers"]["localization optimality test"] = old_bump["check_optimality"]
        new_bump["drivers"]["compute covariance"] = True
        new_bump["drivers"]["compute correlation"] = True
        new_bump["drivers"]["compute localization"] = True

    # Udpate diag_draw_type
    if "diag_draw_type" in old_bump:
        new_bump["sampling"]["draw_type"] = old_bump["diag_draw_type"]

    # Udpate samp_interp_type
    if "samp_interp_type" in old_bump:
        new_bump["sampling"]["interp_type"] = old_bump["samp_interp_type"]

    # Udpate vbal
    if "vbal_block" in old_bump:
        vbal_block = old_bump["vbal_block"]
        if "vbal_diag_auto" in old_bump:
            vbal_diag_auto = old_bump["vbal_diag_auto"]
        else:
            vbal_diag_auto = np.full((len(vbal_block)), False)
        if "vbal_diag_reg" in old_bump:
            vbal_diag_reg = old_bump["vbal_diag_reg"]
        else:
            vbal_diag_reg = np.full((len(vbal_block)), False)
        if "vbal_id_coef" in old_bump:
            vbal_id_coef = old_bump["vbal_id_coef"]
        else:
            vbal_id_coef = np.ones((len(vbal_block)))
        ib = 0
        vbal = []
        for ii in range(1, 10):
            for jj in range(0, ii):
                if ib < len(vbal_block):
                    if vbal_block[ib]:
                        block = {}
                        block["balanced"] = args.variables[ii]
                        block["unbalanced"] = args.variables[jj]
                        if vbal_diag_auto[ib]:
                            block["diag_auto"] = True
                        if vbal_diag_reg[ib]:
                            block["diag_reg"] = True
                        if "vbal_id_coef" in old_bump:
                            block["id_coef"] = vbal_id_coef[ib]
                        vbal.append(block)
                ib += 1
        new_bump["vertical balance"]["vbal"] = vbal

    # Update stddev and var_rhflt
    for key in ["stddev", "var_rhflt"]:
        if key in old_bump:
            vec = []
            for item in old_bump[key]:
                block = {}
                block["variables"] = [item]
                if len(old_bump[key][item]) == 1:
                    block["value"] = old_bump[key][item][0]
                else:
                    block["profile"] = old_bump[key][item]
                vec.append(block)
            new_bump["variance"][key] = vec

    # Update rh, rv, min_lev and max_lev
    for key in ["rh", "rv", "min_lev", "max_lev"]:
        if key in old_bump:
            vec = []
            for item in old_bump[key]:
                block = {}
                block["variables"] = [item]
                if len(old_bump[key][item]) == 1:
                    block["value"] = old_bump[key][item][0]
                else:
                    block["profile"] = old_bump[key][item]
                vec.append(block)
            new_bump["nicas"][key] = vec

    # Update nicas_interp_type
    if "nicas_interp_type" in old_bump:
        vec = []
        for item in old_bump["nicas_interp_type"]:
            block = {}
            block["variables"] = [item]
            block["type"] = old_bump["nicas_interp_type"][item]
            vec.append(block)
        new_bump["nicas"]["interp_type"] = vec

    # Update loc_wgt
    if "loc_wgt" in old_bump:
        vec = []
        for item in old_bump["loc_wgt"]:
            block = {}
            block["row variables"] = [item.split('-')[0]]
            block["column variables"] = [item.split('-')[1]]
            block["value"] = old_bump["loc_wgt"][item]
            vec.append(block)
        new_bump["nicas"]["loc_wgt"] = vec

    # Update dirac section
    if "ndir" in old_bump:
        vec = []
        done = False
        if "grids" in old_bump:
            for grid in old_bump["grids"]:
                if "variables" in grid:
                    for i in range(old_bump["ndir"]):
                        dirac_point = {}
                        dirac_point["longitude"] = old_bump["londir"][i]
                        dirac_point["latitude"] = old_bump["latdir"][i]
                        dirac_point["level"] = old_bump["levdir"][i]
                        dirac_point["variable"] = grid["variables"][old_bump["ivdir"][i]-1]
                        vec.append(dirac_point)
                    done = True
        if not done:
            for i in range(old_bump["ndir"]):
                dirac_point = {}
                dirac_point["longitude"] = old_bump["londir"][i]
                dirac_point["latitude"] = old_bump["latdir"][i]
                dirac_point["level"] = old_bump["levdir"][i]
                dirac_point["variable"] = args.variables[old_bump["ivdir"][i]-1]
                vec.append(dirac_point)
        new_bump["dirac"] = vec

    # Remove empty sections
    for section in sections:
        if not new_bump[section]:
            del new_bump[section]

    # Copy other sections
    for other_section in other_sections:
        if other_section in old_bump:
            new_bump[other_section] = old_bump[other_section]

    # Reset bump
    bumps[i] = new_bump

# Transform bump section into text vectors
bumps_text = []
for i in range(len(bumps)):
    file_tmp = open('tmpfile', 'w')
    yaml.dump(bumps[i], file_tmp, sort_keys=False)
    file_tmp.close()
    file_in = open('tmpfile', 'r')
    text = []
    for line in file_in:
       text.append(line)
    file_in.close()
    os.remove('tmpfile')
    bumps_text.append(text)

# Rename file
os.rename(args.filename, args.filename + ".bak")

# Read and rewrite file, updating the bump sections only
file_in = open(args.filename + ".bak", 'r')
file_out = open(args.filename, 'w')
i = 0
blank = ' '
ind_target = -1
for line in file_in:
    ind_current = len(line)-len(line.lstrip(' '))
    if "bump:" in line and not line.startswith("#"):
        ind_target = ind_current
        text = bumps_text[i]
        file_out.writelines(line)
        for newline in text:
            file_out.writelines((ind_target+2)*blank + newline)
        i += 1
    else:
        if ind_current <= ind_target:
            ind_target = -1
        if ind_target == -1:
            file_out.writelines(line)
file_in.close()
file_out.close()

# Remove backup file
os.remove(args.filename + ".bak")
