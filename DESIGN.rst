Design
======

Below I describe the high-level design of PyNodes.

I build up the model from basic principles, starting
with a description of the conceptual model, followed 
by a description of the semantics I want out of an 
active model instance.

From there I then describe in general computing
terms a representation of the model, the data
structures, functions, and other details that
would be necessary for an implementation of the 
model.

With the computational model complete, I then move
on to the target language, in this case, Python.
I describe the Python specific data types and functions 
that would map to the computation model, taking care
to point out why I selected a particular implementation 
where multiple options are available.

In the penultimate step, a Python graph now implemented,
I describe the interface (API) through which the user
primarily interacts with it with the goal being to keep
that interface as Pythonic and easy to use as possible.
(I define "easy-to-use" to mean the implementation
that requires the least amount of API overhead and user
knowledge to be used effectively, put another way,
the least number of API endpoints and design semantics
a user must keep in mind so that using the graph 
requires little to no reference material above what
would be easy to keep in one's memory.)

I close with a description of addition features
that I will add as part of the implementation or 
at a later phase, particularly those well suited
to a graph.

The Graph: Conceptual Model
---------------------------

* The core concept is that of a directed, acyclic
  graph.

* All nodes on the graph represent functionally pure, 
  side-effect free, statically defined computations. 

* Some subset of these nodes can be dymaically fixed 
  by a user to a particular value, in which case the 
  practical result is that the node now acts as if its
  computation had been defined as a constant
  expression returning that value.

* Fixing a node value does not remove the reference
  to its underlying statically defined computation,
  and any fixed node can have its node unfixed, in
  which case the node reverts to leveraging the former
  computation.
 
* Notwithstanding the above, a user may
  override for any node the semantics of what it means
  to fix a value on that node, subject to following 
  constraints: regardless the overall semantics, 
  the only semantics allowed with respect to graph
  manipulation are those whose effects are logically
  equivilant to the user's having fixed the value of
  zero or more other nodes, one at a time, in a 
  particular order (and without further overrides)
  using any valid value.

  That is to say, a user who defines his own semantics
  for what it means to fix a node, insofar as those
  semantics apply to the graph, is essentially intercepting
  the original fixing and, in its lieu, fixing a set 
  of other nodes with, for each, any valid value.

  For this reason I will call the overriding of
  these semantics a delegate, as the user is essentially
  delegating the logic of which nodes are fixed to
  some other semantics.
  
* A directed edge in the graph from a source node
  to a target node indicates that the value returned
  by evaluating the source computation is used
  as an input in the target computation.
  
* We call the target nodes of the outgoing edges of
  a node its outputs; we call the source node of the
  incoming edges of a node its inputs.

 

The Graph: Runtime Model 
------------------------
* We maintain an in-memory directed, acyclic graph,
  initially empty (no nodes or edges).
