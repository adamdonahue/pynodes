pynodes
=======

Note: Under development.

A Python-based development ecosystem for quickly writing and delivering
business-critical software on the Web and on native platforms.

Example
-------

.. code:: python

 class Person(nodes.GraphEnabled):

     @nodes.graphMethod(nodes.Stored)
     def Name(self):
        return None

     @nodes.graphMethod(nodes.Stored)
     def PublicKey(self):
         return None

     @nodes.graphMethod(nodes.Settable)
     def PrivateKey(self):
         return None

 class EncryptedMessage(nodes.GraphEnabled):

     @nodes.graphMethod(nodes.Stored)
     def From(self):
         return None

     @nodes.graphMethod(nodes.Stored)
     def To(self):
         return None

     def setBody(self, value):
         return [nodes.NodeChange(self._BodyStored, encrypt(value, self.To().PublicKey()))]

     @nodes.graphMethod(delegate=setBody)
     def Body(self):
         if not self.To().PrivateKey():
             raise RuntimeError("No private key has been set for %s!" % self.To().Name())
         return decrypt(self._BodyStored(), self.To().PrivateKey())

     @nodes.graphMethod(nodes.Stored)
     def _BodyStored(self):
         return ''

 alice = Person(Name='Alice', PublicKey=...)
 bob = Person(Name='Bob', PublicKey=...)

 message = EncryptedMessage(From=alice, To=bob)
 message.Body = "The president is on the line."

 print message._BodyStored()    # Encrypted.
 print message.Body()           # <error>  (No private key has been set for Alice!)

 alice.PrivateKey = ...

 print message.Body()           # "The president is on the line.

Components
----------

* An object-oriented, graph-based programming library with built-in dependency tracking, memoization, lazy evaluation, "what if" scenario creation and computation, database integration, and other features.
* A graph database with both native and RESTful APIs.
* A job specification, scheduling, and execution engine.
* A grid computation framework.
* Libraries for rapid web UI creation.
* A bitemporal, fully rewindable event model.
* A timeseries interface with reactive components.
* Domain-specific class sets for trading, advertising, and systems configurations.
