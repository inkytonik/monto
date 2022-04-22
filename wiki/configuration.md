This page describes the configuration process for [Monto](https://bitbucket.org/inkytonik/monto).

Readers should read the [architecture description](architecture.md) first.
Also, see the [Python reference implementation](python.md) for information
about message formats and sources, servers and sinks that can be used for
debugging.

Monto script (`monto.py`)
-------------------------

The Monto script is a convenience script for starting up and stopping the
Monto broker and related programs such as servers and sinks.
The script can be invoked as follows:

* `monto.py` or `monto.py start`: start the programs that are described in the user's .monto configuration file (see below).

* `monto.py stop`: stop the programs (if any) that were started by `monto.py start`.

* `monto.py status`: print a description of the Monto programs that are currently running.

* `monto.py restart`: same as `monto stop` followed by `monto start`.

`.monto` configuration file
---------------------------

A `.monto` file in the user's home directory is used by the Monto script to decide which programs to start. The file is in JSON form and at a minimum has the following structure:

    {
        "programs": [
            {
                "command": "broker.py"
            },
            {
                "command": "/my/path/to/file/reverse.py"
            },
            {
                "command": [ "wrap.py", "wc", "text", "wc", "-l"]
            }
        ]
    }

In this case the configuration specifies that the Monto script should run the Python broker, a server `reverse.py`, and a wrapped server version of the `wc` command.

There is no requirement that the programs be servers, so this method can be
used to start Monto sinks as well.
Be aware that the standard input, output and error of the programs are
redirected to and from `/dev/null` so sinks must use some other mechanism
to communicate with the user if they are started by the Monto script.

The programs inherit the environment of the Monto script so variables such
as `PATH` will be available to find the commands that are specified using
relative paths.
Alternatively, the command name can be specified with an absolute path name
as in the reverse example above.

Program working directory
-------------------------

A program configuration can also include a "directory" specification which
specifies the working directory to be used when that program is executed.
For example,

    {
        "directory": "/Users/asloane/Projects/Monto/scala/length",
        "command": [ "sbt", "run" ]
    }

means that the working directory will be changed to that location before sbt is executed.

Connection addresses
--------------------

The Monto components use network communication to talk to each other.
By default, they use ports 5000-5003 on the local machine.
The Monto configuration file can be used to specify alternative addresses
by including a section with the following form at the top level.

    "connections" : {
        "from_sources" : "tcp://127.0.0.1:8000",
        "to_servers"   : "tcp://127.0.0.1:8001",
        "from_servers" : "tcp://127.0.0.1:8002",
        "to_sinks"     : "tcp://127.0.0.1:8003"
    }

