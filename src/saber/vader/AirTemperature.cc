/*
 * (C) Crown Copyright 2022 Met Office
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 */

#include "saber/vader/AirTemperature.h"

#include <memory>
#include <string>
#include <vector>

#include "atlas/array.h"
#include "atlas/field.h"

#include "eckit/exception/Exceptions.h"

#include "mo/control2analysis_linearvarchange.h"

#include "oops/base/Variables.h"
#include "oops/util/Timer.h"

#include "saber/oops/SaberOuterBlockBase.h"

namespace saber {
namespace vader {

// -----------------------------------------------------------------------------

static SaberOuterBlockMaker<AirTemperature> makerAirTemperature_("mo_air_temperature");

// -----------------------------------------------------------------------------

AirTemperature::AirTemperature(const oops::GeometryData & outerGeometryData,
                               const std::vector<size_t> & activeVariableSizes,
                               const oops::Variables & outerVars,
                               const Parameters_ & params,
                               const atlas::FieldSet & xb,
                               const atlas::FieldSet & fg,
                               const std::vector<atlas::FieldSet> & fsetVec)
  : innerGeometryData_(outerGeometryData), innerVars_(outerVars), augmentedStateFieldSet_()
{
  oops::Log::trace() << classname() << "::AirTemperature starting" << std::endl;

  // Need to setup derived state fields that we need.
  std::vector<std::string> requiredStateVariables{"exner_levels_minus_one",
                                                  "potential_temperature"};

  std::vector<std::string> requiredGeometryVariables{"height_levels",
                                                     "height"};

  // Check that they are allocated (i.e. exist in the state fieldset)
  // Use meta data to see if they are populated with actual data.
  for (auto & s : requiredStateVariables) {
    if (!xb.has(s)) {
      oops::Log::info() << "AirTemperature variable " << s <<
                           " is not part of state object." << std::endl;
    }
  }

  augmentedStateFieldSet_.clear();
  for (const auto & s : requiredStateVariables) {
std::cout << "Test " << s << std::endl;
    augmentedStateFieldSet_.add(xb[s]);
std::cout << "OK test " << s << std::endl;
  }

  for (const auto & s : requiredGeometryVariables) {
std::cout << "Test 2 " << s << std::endl;
    augmentedStateFieldSet_.add(outerGeometryData.fieldSet()[s]);
std::cout << "OK test 2 " << s << std::endl;
  }

  oops::Log::trace() << classname() << "::AirTemperature done" << std::endl;
}

// -----------------------------------------------------------------------------

AirTemperature::~AirTemperature() {
  oops::Log::trace() << classname() << "::~AirTemperature starting" << std::endl;
  util::Timer timer(classname(), "~AirTemperature");
  oops::Log::trace() << classname() << "::~AirTemperature done" << std::endl;
}

// -----------------------------------------------------------------------------

void AirTemperature::multiply(atlas::FieldSet & fset) const {
  oops::Log::trace() << classname() << "::multiply starting" << std::endl;
  mo::evalAirTemperatureTL(fset, augmentedStateFieldSet_);
  oops::Log::trace() << classname() << "::multiply done" << std::endl;
}

// -----------------------------------------------------------------------------

void AirTemperature::multiplyAD(atlas::FieldSet & fset) const {
  oops::Log::trace() << classname() << "::multiplyAD starting" << std::endl;
  mo::evalAirTemperatureAD(fset, augmentedStateFieldSet_);
  oops::Log::trace() << classname() << "::multiplyAD done" << std::endl;
}

// -----------------------------------------------------------------------------

void AirTemperature::calibrationInverseMultiply(atlas::FieldSet & fset) const {
  oops::Log::info() << classname()
                    << "::calibrationInverseMultiply not meaningful so fieldset unchanged"
                    << std::endl;
}

// -----------------------------------------------------------------------------

void AirTemperature::print(std::ostream & os) const {
  os << classname();
}

// -----------------------------------------------------------------------------

}  // namespace vader
}  // namespace saber
