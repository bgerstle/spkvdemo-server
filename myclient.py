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

import sys
import random

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol

random.seed()

class PubSubClient1(WampClientProtocol):

   def onSessionOpen(self):
      self.prefix("pups", "http://spkvexample.com/pups")
      self.addPuppy()

   ## Make changes to the list of dogs here, then run the script to publish them to the server
   ## NOTE: currently the client is hard-coded to talk to localhost
   def addPuppy(self):
      self.publish("pups:/", {
         str(15): {
            "name": "Dozer", 
            "about": "Victorian bulldog", 
            "favorite": False
         }
         # , str(13): {
         #    "name": "Mozart", 
         #    "about": "The prodigal pup", 
         #    "favorite": False  
         # }
      })


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = WampClientFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = PubSubClient1

   connectWS(factory)

   reactor.run()