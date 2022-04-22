This page describes the Python reference implementation of [Monto](https://bitbucket.org/inkytonik/monto).

Readers should read the [architecture description](architecture.md) first.

Installation
------------

The package has been tested with Python 3.6 and requires the following libraries that don't come with the Python distribution: psutil and pyzmq.
You should be able to install those packages using:

    pip3 install psutil
    pip3 install zmq

Install the package itself by running the provided `setup.py`.

Monto library (`montolib.py`)
-----------------------------

The Monto library is a Python implementation of basic functionality for Monto brokers, sources, servers and sinks. If you wish to write one of these processes in Python, you should be able to concentrate on the core of the process without having to worry about details of communication. See the code of the programs below for details on how to use the library.


Sample sources, servers and sinks
---------------------------------

The following scripts use the Monto library to provide simple sources, servers and sinks for debugging purposes.

* `send.py`: a source that takes a file name and sends the current contents of that file as a version.

* `length.py` a server that returns the length of any version it receives (product: "length").

* `reverse.py`: a server that returns a product that is contains the reverse contents of any version that it receives (product: "reverse").

* `reflect.py`: a server that reflects versions back as products with identical contents (product: "reflect").

* `print.py`: a sink that just prints out the products that it receives

Wrapping shell commands
-----------------------

The script `wrap.py` provides an easy way to turn any shell command into a Monto server. The idea is that the shell command reads input from a published version and responds with some text that constitutes the contents of the product produced by the server.

The wrap script supplies the contents of a received version as the standard input to the shell command. The standard output of the shell command is used as the contents of the product.

The simplest form of invocation of the wrap script is to supply the following arguments:

* product: the name of the product that this wrapped command produces

* product language: the name of the language in which the product is written

* command: the shell command to run

* args: zero or more arguments to supply to the shell command

For example, the server configuration

    {
        "command": [ "wrap.py", "wc", "text", "wc", "-l"]
    }

sets up a server that will react to versions by running their contents through the `wc -l` command to count the number of lines. A `wc` product is produce. No specific language is used so `text` is specified.

The default for a wrapped command is to react to versions in any language. A `-v` option can be used to specify the language of versions that this wrapped command can deal with. E.g., if `-v haskell` is specified then the server will only react to Haskell versions.

The wrap script supports some special arguments that enable the behaviour to be customised. The following special arguments are supported:

* `$CONTENTS`: an argument that contains the contents of the version. Useful if the command needs to access the contents via an argument instead of via standard input,

* `$LANGUAGE`: the language of the version,

* `$SELECTION`: the text of the selection in the contents, and

* `$SOURCE`: the identification of the source from which the version comes.

For example, the following server configuration wraps the Haskell hoogle API search command. The hoogle command is given the selection so that it can search for exactly the text that the user has selected.

    {
        "command": [ "wrap.py", "-v", "haskell", "hoogle", "haskell", "hoogle", "$SELECTION" ]
    }
