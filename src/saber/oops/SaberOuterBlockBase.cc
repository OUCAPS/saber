/*
 * (C) Copyright 2021 UCAR
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 */

#include "saber/oops/SaberOuterBlockBase.h"

#include <map>
#include <memory>
#include <string>
#include <vector>

#include "atlas/field.h"
#include "atlas/functionspace.h"

#include <boost/noncopyable.hpp>

#include "oops/base/Variables.h"
#include "oops/util/abor1_cpp.h"
#include "oops/util/AssociativeContainers.h"
#include "oops/util/Logger.h"
#include "oops/util/parameters/OptionalParameter.h"
#include "oops/util/parameters/Parameter.h"
#include "oops/util/parameters/Parameters.h"
#include "oops/util/parameters/RequiredParameter.h"
#include "oops/util/parameters/RequiredPolymorphicParameter.h"
#include "oops/util/Printable.h"

#include "saber/oops/SaberOuterBlockParametersBase.h"

namespace saber {

// -----------------------------------------------------------------------------

SaberOuterBlockBase::SaberOuterBlockBase(const eckit::Configuration & conf)
  : name_(conf.getString("saber block name")) {}


SaberOuterBlockBase::SaberOuterBlockBase(const eckit::Configuration & conf,
                                         const oops::Variables & inputvariables,
                                         const atlas::FunctionSpace & functionSpace,
                                         const atlas::FieldSet & fset) :
    inputVars_(inputvariables), inputFunctionSpace_(functionSpace),
    inputExtraFields_(fset),
    name_(conf.getString("saber block name")) {}

// -----------------------------------------------------------------------------

SaberOuterBlockFactory::SaberOuterBlockFactory(const std::string & name) {
  if (getMakers().find(name) != getMakers().end()) {
    oops::Log::error() << name << " already registered in saber::SaberOuterBlockFactory."
                       << std::endl;
    ABORT("Element already registered in saber::SaberOuterBlockFactory.");
  }
  getMakers()[name] = this;
}

// -----------------------------------------------------------------------------

SaberOuterBlockBase * SaberOuterBlockFactory::create(const eckit::mpi::Comm & comm,
                             const atlas::FunctionSpace & outputFunctionSpace,
                             const atlas::FieldSet & outputExtraFields,
                             const std::vector<size_t> & activeVariableSizes,
                             const eckit::Configuration & conf,
                             const atlas::FieldSet & xb,
                             const atlas::FieldSet & fg,
                             const std::vector<atlas::FieldSet> & fsetVec) {
  oops::Log::trace() << "SaberOuterBlockBase::create starting" << std::endl;
  const std::string id = conf.getString("saber block name");
  typename std::map<std::string, SaberOuterBlockFactory*>::iterator jsb = getMakers().find(id);
  if (jsb == getMakers().end()) {
    oops::Log::error() << id << " does not exist in saber::SaberOuterBlockFactory." << std::endl;
    ABORT("Element does not exist in saber::SaberOuterBlockFactory.");
  }
  SaberOuterBlockBase * ptr = jsb->second->make(comm, outputFunctionSpace, outputExtraFields,
                 activeVariableSizes, conf, xb, fg, fsetVec);
  oops::Log::trace() << "SaberOuterBlockBase::create done" << std::endl;
  return ptr;
}

// -----------------------------------------------------------------------------

std::unique_ptr<SaberOuterBlockParametersBase>
SaberOuterBlockFactory::createParameters(const std::string &name) {
  typename std::map<std::string, SaberOuterBlockFactory*>::iterator it =
      getMakers().find(name);
  if (it == getMakers().end()) {
    throw std::runtime_error(name + " does not exist in saber::SaberOuterBlockFactory");
  }
  return it->second->makeParameters();
}

// -----------------------------------------------------------------------------

}  // namespace saber
