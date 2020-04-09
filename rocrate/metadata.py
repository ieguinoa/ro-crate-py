#!/usr/bin/env python

## Copyright 2019 The University of Manchester, UK
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import datetime
import warnings
import json
import pkg_resources

# FIXME: Avoid eager loading?
_RO_CRATE = json.load(pkg_resources.resource_stream(__name__, "data/ro-crate.jsonld"))
_SCHEMA = json.load(pkg_resources.resource_stream(__name__, "data/schema.jsonld"))
_SCHEMA_MAP = dict( (e["@id"],e) for e in _SCHEMA["@graph"])

def _term_to_uri(name):
    # NOTE: Assumes RO-Crate's flat-style context
    return _RO_CRATE["@context"][name]

def _schema_doc(uri):
    ## NOTE: Ensure rdfs:comment still appears in newer schema.org downloads
    # TODO: Support terms outside schema.org?
    return _SCHEMA_MAP[uri].get("rdfs:comment", "")

from .utils import *

"""
RO-Crate metadata file

This object holds the data of an RO Crate Metadata File rocrate_

.. _rocrate: https://w3id.org/ro/crate/0.2
"""

class _Entity(object):
    def __init__(self, identifier, metadata):
        self.id = identifier
        self._metadata = metadata
        self._entity = metadata._find_entity(identifier)
        if self._entity is None:            
            self._entity = metadata._add_entity(self._empty())

    def __repr__(self):
        return "<%s %s>" % (self.id, self.type)

    def _empty(self):        
        return {     
                    "@id": self.id,
                    "@type": self.type ## Assumes just one type
               }

    def __getitem__(self, key):
        return self._entity[key]

    def __setitem__(self, key, value):
        # TODO: Disallow setting non-JSON values
        self._entity[key] = value

    def __delitem__(self, key):
        del self._entity[key]

    def get(self, key, default=None):
        return self._entity.get(key, default)

    @property
    def type(self):
        return first(self.types)

    @property
    def types(self):
        return tuple(as_list(self.get("@type", "Thing")))

class Thing(_Entity):
    pass


class DataEntity():

class FileDataEntity(DataEntity):


class DirectoryDataEntity(DataEntity):



class ContextEntity(object):

    def __init__(self, entity_constructor=None):
        self.entity_constructor = entity_constructor or Thing

    def getmany(self, instance):
        for json in as_list(instance.get(self.property)):
            # TODO: Support more advanced dispatching
            yield self.entity_constructor(json["@id"], instance._metadata)

    def setmany(self, instance, values):
        json = []
        for value in values:
            ## TODO: Check it has compatible @type?
            if value._metadata != instance._metadata:
                # Oh no, it might have different base URIs, 
                # will need to be added to @graph, reference
                # other objects we don't have etc.
                # TODO: Support setting entities from other RO-Crates
                raise ValueError("Adding entity from other RO-Crate not (yet) supported")
            json.append({"@id": value.id})
        instance[self.property] = flatten(json)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        result = None
        for val in self.getmany(instance):
            if result is not None:
                warnings.warn("More than one value in %s.%s, returning first" % (self.owner, self.property))
                break
            result = val
        return result

    def __set__(self, instance, value):
        # TODO: Check if arrays are permitted
        self.setmany(instance, as_list(value))
    def __delete__(self, instance):
        ## TODO: Check if permitted to delete?
        instance[self.property] = [] # known property, empty in JSON
    def __set_name__(self, owner, name): # requires Py 3.6+
        if not owner.__doc__:
            _set_class_doc(owner)
        self.owner = owner
        self.property = name
        uri = _term_to_uri(name)
        doc = _schema_doc(uri)
        self.__doc__ = "Single contextual entity %s\n%s" % (uri,doc)
        # Register plural _s variant 
        # TODO: Register plural _s variants
        setattr(owner, name+"s", 
            property(self.getmany, self.setmany, 
                     doc="Multiple contextual entities %s\n%s" % (uri,doc)))
        # TODO: Register _ids variants?

def _set_class_doc(Class):
    # set the class documentation
    try:
        # FIXME: avoid this hack here!
        uri = _term_to_uri(Class.__name__)
        doc = _schema_doc(uri)
        Class.__doc__ = "Entity %s\n%s" % (uri,doc)
    except KeyError:
        pass ## Non-matching class name, ignore




class PeopleContextualEntity(ContextualEntity):

    def __init__(self,id_):
        super().__init__(self,identifier)
        self.type = 'Person'


class OrganizationContextualEntity(ContextualEntity):
    def __init__(self,id_):
        super().__init__(self,id_)
        self.type = 'Organization'

class ContactPointContextualEntity(ContextualEntity):
    def __init__(self,id_):
        super().__init__(self,id_)
        self.type = 'ContactPoint'






class Metadata(_Entity):
    def __init__(self):
        self._jsonld = self._template()  ## bootstrap needed by the below!
        super().__init__("ro-crate-metadata.jsonld", self)

    def _template(self):
        # Hard-coded bootstrap for now
        return {
            "@context": "https://w3id.org/ro/crate/0.2/context",
            "@graph": [
                {
                    "@id": "ro-crate-metadata.jsonld",
                    "@type": "CreativeWork",
                    "identifier": "ro-crate-metadata.jsonld",
                    "about": {"@id": "./"}
                },
                {
                    "@id": "./",
                    "@type": "Dataset"
                }
            ]
        }

    def _find_entity(self, identifier):
        for item in self._jsonld["@graph"]:
            if item.get("@id", None) == identifier:
                return item

    def _add_entity(self, entity):
        ## TODO: Check/merge duplicates? Valid by JSON-LD, but 
        # we won't find the second entry again above
        self._jsonld["@graph"].append(entity)
        return entity # TODO: If we merged, return that instead here

    #@property
    #def about(self):
    #    return Dataset("./", self)
    
    # Delayed access trick as we have not defined Dataset yet
    """The dataset this is really about"""
    about = ContextEntity(lambda id,metadata: Dataset(id,metadata))

    @property
    def root(self):
        return self.about

    def as_jsonld(self):
        return self._jsonld

class File(_Entity):
    @property
    def types(self):
        return ("File",) ## Hardcoded for now

class Person(_Entity):
    @property
    def types(self):
        return ("Person",) ## Hardcoded for now

class Dataset(_Entity):
    def __init__(self, identifier, metadata):
        super().__init__(identifier, metadata)
        self.datePublished = datetime.datetime.now() ## TODO: pick it up from _metadata

    @property
    def types(self):
        return ("Dataset",) ## Hardcoded for now

    hasPart = ContextEntity(File)
    author = ContextEntity(Person)

    @property
    def datePublished(self):
        date = self.get("datePublished")
        return date and datetime.datetime.fromisoformat(date)
    
    @datePublished.setter
    def datePublished(self, date):
        if hasattr(date, "isoformat"): # datetime object
            self["datePublished"] = date.isoformat()
        else:
            self["datePublished"] = str(date)

