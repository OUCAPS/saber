/*
 * (C) Crown Copyright 2022 Met Office
 * 
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0. 
 */

#pragma once

#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "atlas/field.h"
#include "atlas/functionspace.h"

#include "oops/base/Variables.h"

namespace saber {
namespace vader {

atlas::Field createGpRegressionMatrices(const std::string &,
                                        const std::size_t,
                                        const std::size_t);

std::vector<double> interpWeights(std::vector<std::vector<double>> &,
                                  std::vector<std::vector<double>> &,
                                  double);

atlas::Field createGpRegressionWeights(const atlas::FunctionSpace &,
                                       const atlas::FieldSet &,
                                       const std::string &,
                                       const std::size_t,
                                       const std::size_t);

void populateInterpMuStats(atlas::FieldSet &,
                           const atlas::Field &);

}  // namespace vader
}  // namespace saber
