class SchemaProperty:

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        #why return the first? 
        # result = None
        # for val in self.getmany(instance):
            # if result is not None:
                # warnings.warn("More than one value in %s.%s, returning first" % (self.owner, self.property))
               # break
            # result = val
        return instance[self.property]

    def __set__(self, instance, value):
        # TODO: Check if arrays are permitted
        #self.setmany(instance, as_list(value))
        instance[self.property] = instance.auto_reference(value)

    def __delete__(self, instance):
        ## TODO: Check if permitted to delete?
        instance[self.property] = [] # known property, empty in JSON

    def __set_name__(self, owner, name): # requires Py 3.6+
        self.property = name # save the property name
        self.owner = owner
        # TODO: review this part
        # check if the class has associated documentation
        # if not owner.__doc__:
            # _set_class_doc(owner)
            # uri = vocabs.term_to_uri(name)
            # doc = vocabs.schema_doc(uri)
            # #review this
            # self.__doc__ = "Single contextual entity %s\n%s" % (uri,doc)
            # # Register plural _s variant 
            # # TODO: Register plural _s variants
            # setattr(owner, name+"s",
                # property(self.getmany, # self.setmany, doc="Multiple contextual entities %s\n%s" % (uri,doc)))
            # # TODO: Register _ids variants?





    # def __get__(self, instance, owner):
        # return instance.__dict__[self.name]
    # def __set__(self, instance, value):
        # if value < 0:
            # raise ValueError('Cannot be negative.')
        # instance.__dict__[self.name] = value
    # def __set_name__(self, owner, name):
        # self.name = name
