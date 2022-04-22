Build Prerequisites
-------------------

The C monto broker is based on a autoconf/automake buildsystem. You need the
following build prerequisites:

 * autoconf
 * automake
 * make
 * libzmq
 * libjson-c


Build Instructions
------------------

You need to generate the configure files, configure the build and finally build
the sources. The build can be done starting with a clean project with the
following steps:

    $ cd monto/c

    $ ./reconf.sh
    configure.ac:6: installing './install-sh'
    configure.ac:6: installing './missing'
    Makefile.am: installing './depcomp'

    $ ./configure
    checking for a BSD-compatible install... /bin/install -c
    checking whether build environment is sane... yes
    ...
    configure: creating ./config.status
    config.status: creating Makefile
    config.status: creating config.h
    config.status: executing depfiles commands

    $ make

If all goes well, the executable of the broker can be found in the subdirectory
of the C broker.

Configuration Options
---------------------

If dependent libraries such as libzmq are stored in directories that are
not searched by default, you will need to specify their location when you
configure the broker. For example, if the library's header file and object
file are located in /usr/local, the following should suffice.

    CFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib ./configure

