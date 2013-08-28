pynodes
=======

Note: Under development.

A Python-based development ecosystem for quickly writing and delivering
business-critical software on the Web and on native platforms.

Synopsis
--------

.. code:: python

    import nodes

    class Person(nodes.GraphEnabled):
        @nodes.graphMethod(nodes.Settable)
        def Name(self):
            return None

        @nodes.graphMethod(nodes.Settable)
        def Scores(self):
            return []

        @nodes.graphMethod
        def AverageScore(self):
            return sum(self.Scores()) / len(self.Scores())

    person = Person(Name='Adam', Scores=[2.0, 1.0])
    print person.AverageScore()

    with nodes.scenario():
        person.Scores.setWhatIf([1.0, 1.0])
        print person.AverageScore()
    print person.AverageScore()

    with nodes.scenario() as s1:
        person.Scores.setWhatIf([2.0])
    with s1:
        print person.AverageScore()
    print person.AverageScore()


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
