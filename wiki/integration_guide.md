Integration Guide
=================

This guide describes how to integrate Monto into a frontend like an IDE or
editor. This guide uses code examples from the integration of Monto into
eclipse but the code should be easy enough to translate it to other
languages, editors or IDEs.


Prerequisites
-------------

Monto communicates with JSON over ZeroMQ, thus a Monto plugin needs
libraries that works with these technologies. Here are sites that list a
huge number of language bindings for these technologies:

 * [ZeroMQ Bindings](http://zeromq.org/bindings:_start)
 * [JSON Bindings](http://www.json.org/)


ZeroMQ connection
-----------------

To make a connection to the Monto broker, a ZeroMQ connection needs to be
established. The plugin has to be able to send version messages and to
receive product messages, therefore two connections are opened. The
following code describes how to correctly setup and tear down these
connections.

```java
// Setup the ZeroMQ context
Context context = ZMQ.context(numberOfThreads);

// Setup a connection that sends version messages
// from sources to the broker
Socket fromSourceSocket = context.socket(ZMQ.REQ);

// The time how long pending messages are kept in
// memory after the connection has been closed.
// This is important for closing the connection,
// else the close method blocks indefinitely.
fromSourceSocket.setLinger(seconds(2));

// Opens the connection on localhost port 5000.
// This is just an example, later this string should
// be read from the Monto configuration file.
fromSourceSocket.connect("tcp://127.0.0.1:5000");

// Setup a connection that receives product messages
// from the broker
toSinksSocket = context.socket(ZMQ.SUB);
toSinksSocket.setReceiveTimeOut(seconds(2));
toSinksSocket.connect("tcp://127.0.0.1:5003");

// Tells the connection to subscribe to all incoming
// messages.
toSinksSocket.subscribe(new byte[]{});


// ...
// Do the work of sending version messages and receiving
// product messages
// ...


// First close the sockets, then the context
fromSourceSocket.close();
toSinksSocket.close();
context.term();
```


Sending version messages
------------------------

The sending of version messages is pretty straight forward. First the
message needs to be converted to a JSON string, that is then send over the
`fromSourcesSocket`. After that the plugin has to wait for an
acknowledgement from the broker, else the request response protocol is
violated.

```java
String json = VersionMessage.encode(message).toJSONString();
fromSourceSocket.send(json);
byte[] ack = fromSourceSocket.recv();

if(hasTimedOut(ack)) {
    // inform the user that the connection is unresponsive,
    // maybe starting the broker.
}
```


Receiving product messages
--------------------------

The process of receiving and processing a product message can be structured
in the following steps:

 * Wait until the message has arrived and the connection has not timed out. 
 * Register that a product for a source is available. This is needed that 
   the UI can present a list to the user with all available products for a
   source.
 * Inform all sinks that a new product message has arrived. The
   parsing of the `content` field is done by the sink.

```java
String response = toSinksSocket.recvStr();
if(hasTimedOut(response)) {

    // inform the user that the connection is unresponsive,
    // maybe return null or throw an exception.

} else {

    ProductMessage message = ProductMessage.decode(response);
    registerProduct(message.getSource(), message.getProduct());
    sinks.forEach(sink -> sink.onProductMessage(message));
}
```


Reading the connection information from the Monto configuration file
--------------------------------------------------------------------

The information for opening the ZeroMQ connection is stored in the
`~/.monto` configuration file. The file may contain a section like this:

```json
"connection" : {
    "from_source" : "tcp://127.0.0.1:5000",
    "to_server"   : "tcp://127.0.0.1:5001",
    "from_server" : "tcp://127.0.0.1:5002",
    "to_sinks"    : "tcp://127.0.0.1:5003",
    "threads"     : 4
}
```

The information can the be obtained like this:

```java
String home = System.getProperty("user.home");
Path montoConfig = FileSystems.getDefault().getPath(home, ".monto");

try {
    JSONObject montoConfig = (JSONObject) JSONValue.parse(readFile(montoConfig));
    JSONObject connectionInfo = (JSONObject) montoConfig.get("connection");
    String fromSource = (String) connectionInfo.get("from_source");
    String toSinks = (String) connectionInfo.get("to_sinks");
    int ioThreads = ((Long) connectionInfo.get("threads")).intValue();

    ... // setup connection

} catch (Exception e) {
    throw new ConnectionParseException(e);
}
```


Encode a version message
------------------------

The encoding of a version message is straight forward. As a reminder, a
version message has to have this structure:

```json
{
    "source": "/foo/bar/DATA1.txt",
    "language": "text",
    "contents": "Hello SLE 2014!!!\\n",
    "selections": [{"begin": 5, "end": 10}]
}
```

```java
JSONObject version = new JSONObject();
version.put("source", message.getSource().toString());
version.put("language", message.getLanguage().toString());
version.put("contents", message.getContent().toString());
JSONArray selections = new JSONArray();
for(Selection selection : message.getSelections()) {
    JSONObject sel = new JSONObject();
    sel.put("begin", selection.getBegin());
    sel.put("end", selection.getEnd());
    selections.add(sel);
}
version.put("selections", selections);
```


Decoding a product message
--------------------------

The product message has this format:

```json
{
    "source": "/foo/bar/DATA1.txt",
    "product": "length",
    "language": "number",
    "contents": "18"
}
```

```java
try {
    JSONObject message = (JSONObject) JSONValue.parse(reader);
    Source source = new Source((String) message.get("source"));
    Product product = new Product((String) message.get("product"));
    Language language = new Language((String) message.get("language"));
    Contents contents = new Content((String) message.get("contents"));
    return new ProductMessage(source, product, language, contents);
} catch (Exception e) {
    throw new ProductMessageParseException(e);
}
```


Source changed
--------------

The following sections depend very closely on the editor or IDE Monto is
integrated in. Therefore the code here is more abstract to explain what to
do.

This section describes what to do if a source has changed. A source can be
a file that is edited in the editor or something else. So the first thing
to find out is how to listen to changes to the source. Then the plugin
needs to perform the following steps:

 * get a unique identifier for the source, like the filename of the edited
   file.
 * find out the language the file is written in. This can be done by
   either asking the API of the editor, looking at the file extension or
   inspecting the contents of the file.
 * get the content of the source, like the text of the edited document.
 * get the start and end of the areas that are currently selected in the
   editor.
 * Construct the message, decode it and send it to the broker.


Present the user available products for a source
------------------------------------------------

This can be done in multiple ways. The Monto-Eclipse plugin has implemented
this by adding a context menu to editor window for a file that contains all
products that are available for the edited file.

![Open Monto product](http://bitbucket.org/inkytonik/monto/raw/default/wiki/select_product.png)

If the user selects a product, the plugin has to open a sink. This can be a
new editor window or something else. The sink has to remember to which
source, language and product it is associated to, since each sink receive
**all** product messages.


Update sinks
------------

The sink needs to decide which messages are relevant to it and needs to
update its content. The sink also needs to display at least the source and
the product that is associated with it, that the user can identify, at
which product he is looking at. The result of opening multiple products can
look like this:

![Opening multiple products](http://bitbucket.org/inkytonik/monto/raw/default/wiki/example_products.png)

**Caution**: Often the thread in which the sink receives the product
message is a different one from the thread that manages the UI. In this
case, the update to the editor content needs to be scheduled to run in the
UI thread.

```java
Display.getDefault().asyncExec(
    () -> editor.set(messageContents)
);
```

**Caution**: If the source and the sink are different windows in the
editor, the sink needs to be read-only. It makes no sense to let the user
make changes to the sink that then get overridden by the next product
message for that sink.
