This page gives an overview of the Monto architecture, including the messages that are used to communicate between processes.

Architecture
------------

The Monto architecture contains separate _source_, _server_ and _sink_ processes. A single _broker_ process coordinates communication between the sources, servers and sinks. The broker exists so that the other processes do not need to be aware of the location or form of each other.

![Monto Architecture](https://bitbucket.org/inkytonik/monto/raw/default/wiki/architecture.png)

As the user makes changes to text such as program source code (step 1), a source process that is monitoring those changes publishes each version (step 2). The broker passes the versions to the servers (step 3). Servers can optionally react to the versions by producing products that are sent back to the broker (step 4). The broker passes all products to the sinks (step 5). Sinks can optionally display the product to the user (step 6).

The current Monto broker sends versions to all servers and products to all sinks. It is up to the server or sink to react appropriately if they can handle the change or response.

Sources and Version Messages
----------------------------

Action in a Monto-based environment begins with a source process that monitors some textual data. A version message is sent by the source to notify servers about that data. A typical source is a text editor that is monitoring the user as they edit files, but any process can generate versions.

Versions can be sent at any appropriate granularity. Some possibilities are: after every keystroke in an editor, after every keystroke and selection change, or periodically whether or not the user has made any change.

A source publishes a version of its source data by sending a _version message_ that contains the following fields:

* source: a unique identifier that identifies the source data. Usually it is the name of the file that is backing the content that is being edited.

* language: the name of the language in which the source is written. Language names are defined by convention.

* contents: the actual content of the version. Note that for source data that is backed by a file the content will often not be the same as the content of the file since the file may not have been saved.

* selections: an array of objects that describe the current selections in the source data. Each object should have fields ‘begin’ and ‘end’ that are numbers to specify the range of a selection, counting from zero at the beginning of the contents. The beginning of a selection should always be less than or equal to the end.

Servers and Product Messages
----------------------------

A Monto server is a process that waits for changes to arrive from the broker and, optionally, responds with a product. The content of a product is usually derived from the version that triggered it. For example, a server that formats source code would react to versions that are written in the language supported by the formatter and response with products that contain the formatted code. A server publishes a product by sending a _product message_ that contains the following fields:

* source: the unique identifier of the source from which this product was derived. Usually the source identifier will be the same as the source identifier of the version that triggered the response.

* product: the name of the product. E.g., for a response that sends the abstract syntax tree for a minijava program the product might be ‘tree’. Monto enforces no particular discipline on the names of products.

* language: the language in which the response text is written. In many cases the response will be not in particular formal language, so ‘text’ is the language. However, for products such as formatted source code it would be appropriate to use the language of that code.

* contents: the contents of the response as text.

Communication
-------------

Monto uses the [ZeroMQ](http://zeromq.org) library to implement communication between processes. Messages are sent in JSON format.

For example, the following is a version message reporting the content of a text file where the characters from position 5 to position 10 are selected:

    {
        "source": "/foo/bar/DATA1.txt",
        "language": "text",
        "contents": "Hello SLE 2014!!!\\n",
        "selections": [{"begin": 5, "end": 10}]
    }

and the following is the content of a product message that contains the length of the source as a number:

    {
        "source": "/foo/bar/DATA1.txt",
        "product": "length",
        "language": "number",
        "contents": "18"
    }


