#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([Monto], [0.0.1], [https://bitbucket.org/inkytonik/monto/issues])
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([broker.c])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile])

# Checks for programs.
AC_PROG_CC

# Checks for libraries.
AC_CHECK_HEADERS(zmq.h,, [AC_MSG_ERROR([zmq.h required])])
AC_CHECK_LIB(zmq, zmq_init, ,[AC_MSG_ERROR([cannot link with -lzmq, install libzmq.])])

AC_CHECK_HEADERS(json-c/json.h,, [AC_MSG_ERROR([json-c/json.h required])])
AC_CHECK_LIB(json-c, json_tokener_new, ,[AC_MSG_ERROR([cannot link with -ljson-c, install json-c.])])

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

AC_OUTPUT
