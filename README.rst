pynodes
=======

Note: Under development.

A Python-based development ecosystem for quickly writing and delivering
business-critical software on the Web and on native platforms.

Synopsis
--------

.. code:: python

    import pynodes
    
    class Person(pynodes.GraphEnabled):
        
        @pynodes.graphEnabled(pynodes.Writable)
        def Name(self):
            return None
            
        @pynodes.graphEnabled(pynodes.Writable)
        def Scores(self):
            return []
            
        @pynodes.graphEnabled
        def AverageScore(self):
            return self.Scores() / len(self.Scores())
        
    person = Person(Name='Adam', Scores=[2.0, 1.0])
    person.AverageScore()     -> 1.5
    
    with pynodes.whatIf():
        person.Scores.setWhatIf([1.0, 1.0])
        person.AverageScore() -> 1.0
    person.AverageScore()     -> 1.5
    
    with pynodes.scenario() as s1:
        person.Scores.setWhatIf([2.0])
    with s1:
        person.AverageScore() -> 2.0
    person.AverageScore()     -> 1.5
    
    person.write('/Persons/' + person.Name())
    
    # More to come.
    
        

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
