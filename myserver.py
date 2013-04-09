###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys, json, os, pdb

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, \
                          WampServerProtocol, \
                          exportRpc, \
                          exportSub, exportPub


class PupStorage:
   protocol = None
   path = None

   def __init__(self, filepath):
      self.path = filepath
      f = open(filepath, 'r')
      self.store = json.load(f)
      f.close()

   def _get_all(self):
      return self.store

   def writeToDisk(self):
      f = open(self.path, 'w')
      f.write(json.dumps(self.store))
      f.close()

   @exportRpc
   def get(self, pup_id=None):
      if pup_id == None:
         return self._get_all()
      return self.store[pup_id];

   @exportSub("/", True)
   def sub(self, topicURIPrefix, topicURISuffix):
      return True

   @exportPub("/", True)
   def set(self, topicURIPrefix, topicURISuffix, event):
      try:
         for key, values in event.iteritems():
            #pdb.set_trace()
            if key in self.store:
               if len(values) == 0:
                  print "Deleting pup {0}".format(self.store[key])
                  del self.store[key]  
               else:
                  pup = self.store[key]
                  pup.update(values)
            else:
               self.store[key] = values
         return event
      except Exception, e:
         print repr(e)
      return None

class PupServerProtocol(WampServerProtocol):

   def onSessionOpen(self):
      ## register a URI and all URIs having the string as prefix as PubSub topic
      self.registerHandlerForPubSub(self.factory.pupStorage, "http://spkvexample.com/pups")

      self.registerForRpc(self.factory.pupStorage, "http://spkvexample.com/pups#")
      self.factory.pupStorage.protocol = self;

   def onClose(self, wasClean, code, reason):
      self.factory.pupStorage.writeToDisk()


class PupServerFactory(WampServerFactory):
   pupStorage = None

if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = True#len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = PupServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.pupStorage = PupStorage("{0}/{1}".format(os.path.dirname(os.path.realpath(__file__)), "pups.json"))
   factory.protocol = PupServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()