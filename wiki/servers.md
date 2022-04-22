This page lists servers and related code that can operate in a Monto-based
development environment.
Servers sit between sources and sinks with which the user is interacting,
possibly via an integrated
[frontend](https://bitbucket.org/inkytonik/monto/src/default/wiki/frontends.md).

Scala server support
--------------------

The following projects provide useful support for building Monto servers in
Scala:

* [MontoScala](https://bitbucket.org/inkytonik/montoscala): generic support
for Monto servers

* [MontoKiama](https://bitbucket.org/inkytonik/montokiama): builds on
MontoScala to add specific support for servers that are based on the
compiler framework of the [Kiama language processing
library](https://bitbucket.org/inkytonik/kiama)

MiniJava
--------

This [MiniJava Compiler Server](https://bitbucket.org/inkytonik/montominijava)
wraps the MiniJava example from the Kiama tests to be a Monto server.

MontoCoq
--------

An [experimental Monto server](https://bitbucket.org/inkytonik/montocoq) to
support interactive proof using the Coq proof assistant.
