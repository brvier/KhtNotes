# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Handling for privileges for grant and deny clauses in ACEs 
according to WebDAV ACP specification.
"""


from webdav import Constants
from webdav.Connection import WebdavError


__version__ = "$LastChangedRevision$"


class Privilege(object):
    """This class provides functionality for handling privileges for ACEs.
     
    @ivar name: Name of the privilege.
    @type name: C{string}
    
    @cvar __privileges: List of allowed XML tags for privileges.
    @type __privileges: C{tuple} of C{string}s
    """


    __privileges = list()
        
    
    def __init__(self, privilege=None, domroot=None):
        """
        Constructor should be called with either no parameters (create blank Privilege),
        one parameter (a DOM tree or privilege name to initialize it directly).
        
        @param domroot: A DOM tree (default: None).
        @type  domroot: L{webdav.WebdavResponse.Element} object
        @param privilege: The valid name of a privilege (default: None).
        @type  privilege: C{string}
        
        @raise WebdavError: When non-valid parameters or sets of parameters are 
                            passed a L{WebdavError} is raised.
        """
        
        self.name = None
        
        if domroot:
            if len(domroot.children) != 1:
                raise WebdavError('Wrong number of elements for Privilege constructor, we have: %i' \
                    % (len(domroot.children)))
            else:
                child = domroot.children[0]
                if child.ns == Constants.NS_DAV and child.name in self.__privileges:
                    self.name = child.name
                else:
                    raise WebdavError('Not a valid privilege tag, we have: %s%s' \
                        % (child.ns, child.name))
        elif privilege:
            if privilege in self.__privileges:
                self.name = privilege
            else:
                raise WebdavError('Not a valid privilege tag, we have: %s.' % str(privilege))

    @classmethod
    def registerPrivileges(cls, privileges):
        """
        Registers supported privilege tags.
        
        @param privileges: List of privilege tags.
        @type privileges: C{list} of C{unicode}
        """
        
        for privilege in privileges:
            cls.__privileges.append(privilege)
    
    def __cmp__(self, other):
        """ Compares two Privilege instances. """
        if not isinstance(other, Privilege):
            return 1
        if self.name != other.name:
            return 1
        else:
            return 0

    def __repr__(self):
        """ Returns the string representation of an instance. """
        return '<class Privilege: name: "%s">' % (self.name)

    def copy(self, other):
        """
        Copy Privilege object.
        
        @param other: Another privilege to copy.
        @type  other: L{Privilege} object
        
        @raise WebdavError: When an object that is not a L{Privilege} is passed 
            a L{WebdavError} is raised.
        """
        if not isinstance(other, Privilege):
            raise WebdavError('Non-Privilege object passed to copy method: %s' % other.__class__)
        self.name = other.name

    def toXML(self):
        """
        Returns privilege content as string in valid XML as described in WebDAV ACP.
        
        @param defaultNameSpace: Name space (default: None).
        @type  defaultNameSpace: C(string)
        """
        assert self.name != None, "privilege is not initialized or does not contain valid content!"
        
        privilege = 'D:' + Constants.TAG_PRIVILEGE
        return '<%s><D:%s/></%s>' % (privilege, self.name, privilege)
