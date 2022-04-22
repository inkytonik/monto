This page describes products that Monto servers can return.
Since Monto does not prescribe any particular naming convention for
products or structure for product contents, this page acts as a central
point for developing community conventions.

Product Languages
-----------------

Wherever possible the language used for a product should use the full
lower-case name of the language in which the product content is written.
For example, the output of the Hoogle shell command contains Haskell
function signatures, so the language should be `"haskell"`.

If the product content is written in no particular formal language,
then the language name `"text"` should be used.

Products from Shell Commands
----------------------------

If the content of a product is coming from a shell command then our
convention is to use the name of the command in lower-case as the product
name and the text content of the output of the shell command as the product
contents.
For example, if the `hoogle` command is used to generate a product
containing Hoogle search results, then the name of the production would be
`"hoogle"` and the contents would be the Hoogle result output.

Tokenization Products
---------------------

This product describes the positions, length and category of tokens a given
source consists of. For instance this information can be used to implement
syntax highlighting for a programming language.

An example of a tokenization product of a Java file could look this. A
version message gets send to the servers like usual.

```json
{
   "source": "Foo.java",
   "language": "java",
   "contents": "public class Foo { ..."
}
```

The server that implements the tokenization answers in the following format.

```json
{
   "source": "Foo.java",
   "product": "tokens",
   "language": "json",
   "contents": [
     { "offset": 0,  "length": 6, "category": "modifier"   },
     { "offset": 7,  "length": 4, "category": "structure"  },
     { "offset": 12, "length": 3, "category": "identifier" },
     ...
   ]
}
```

In order for a frontend to be able to implement syntax highlighting, the
allowed values for the token category have to be element of a predefined
set. The Monto project proposes the following categories that are derived
from [vim](http://vimdoc.sourceforge.net/htmldoc/syntax.html#group-name).

```text
comment:        any comment

constant:       any constant
string:         a string constant, "this is a string"
character:      a character constant, 'c', '\n'
number:         a number constant, 234, 0xff
boolean:        a boolean constant, TRUE, false
float:          a floating point constant, 2.3e10

identifier:     any variable name

statement:      any statement
conditional:    if, then, else, endif, switch, etc.
repeat:         for, do, while, continue, break, etc.
label:          case, default, etc.
operator:       sizeof, +, *, etc.
keyword:        any other keyword
exception:      try, catch, throw

type:           int, long, char, etc.
modifier:       public, private, static, etc.
structure:      struct, union, enum, class etc.

punctuation:    any non alphanumeric tokens that are no operators.
parenthesis:    () [] {}, <> etc.
delimiter:      , . ; etc.

meta:           C preprocessor macros, Java Annotations, etc

whitespace:     Non visible character

unknown:        Unknown token, can occur during text insertion
```

The predefined categories are organized in hierarchies to make it easier
for users to build color schemes. For example each `number` literal is also
a `constant`. The user can now choose to set a color for all constants or
to give number literals a different color. The following graphic describes
visually the hierarchies of categories, where an arrow from `A` to `B`
means that `B` is-a `A`.

![Token Category Hierarchy](https://bitbucket.org/inkytonik/monto/raw/default/wiki/token_category_hierarchy.svg)


Abstract Syntax Tree Products
-----------------------------

An abstract syntax tree (AST) conveys useful information about the structure of
a program. An AST is an ordered tree with labeled nodes and tokens at its leafs.
The grammar of a programming language defines the variations an AST can have.

To give an example of arithmetic expressions, the grammar can be described in
Backus-Naur-Form:

```
<addition>       ::= <multiplication>
                   | <addition> "+" <addition>
                   | <addition> "-" <addition>

<multiplication> ::= <factor>
                   | <multiplication> "*" <multiplication>
                   | <multiplication> "/" <multiplication>

<factor>         ::= <number> | "(" <addition> ")"
<number>         ::= any number
```

For example the arithmetic expression `1 * 2 + 3 * 4` produces the following
AST:

![AST](https://bitbucket.org/inkytonik/monto/raw/default/wiki/ast.svg)

The JSON format for the AST uses arrays to preserve ordering where the first
element of the array is the name of the non terminal rule of the grammar. Tokens
or terminals are represented as above with offset and length. The example of
above is encoded in the following way:

```json
{
  "source": "arithexprs.txt",
  "product": "ast",
  "language": "json",
  "contents":
    [ "addition",
      [ "addition",
        [ "multiplication",
          [ "multiplication",
            [ "factor",
              [ "number",
                { "offset": 0, "length": 1 }
              ]
            ]
          ],
          { "offset": 2, "length": 1 },
          [ "multiplication",
            [ "factor",
              [ "number",
                { "offset": 4, "length": 1 },
              ]
            ]
          ]
        ]
      ],

      { "offset": 6, "length": 1 },

      [ "addition",
        [ "multiplication",
          [ "multiplication",
            [ "factor",
              [ "number",
                { "offset": 8, "length": 1 }
              ]
            ]
          ],
          { "offset": 10, "length": 1 }
          [ "multiplication",
            [ "factor",
              [ "number",
                { "offset": 12, "length": 1 }
              ]
            ]
          ]
        ]
      ]
    ]
}
```


Outline Products
----------------

Browsing very large code documents can be very confusing. An outline view gives
a good overview of the document and allows quick jumping to relevant places.

![Outliner](https://bitbucket.org/inkytonik/monto/raw/default/wiki/outline_product.png)

Each item in the outline contains an icon that represents the category of the
item and an label that links directly into the document. The example in the
image can be encoded as the following JSON document:

```json
{
  "source": "hello.java"
  "product": "outline",
  "language": "json",
  "contents":
    {
      "description": "compilationUnit",
      "label": {"offset": 0,"length": 245},
      "childs": [
        {
          "description": "package",
          "label": {"offset": 8,"length": 5},
          "icon": "/fullpathto/packd_obj.gif"
        },
        {
          "description": "class",
          "label": {"offset": 29,"length": 10},
          "icon": "/fullpathto/class_obj.gif",
          "childs": [
            {
              "description": "field",
              "label": {"offset": 72,"length": 11},
              "icon": "/fullpathto/methpri_obj.gif"
            },
            {
              "description": "method",
              "label": {"offset": 123,"length": 13},
              "icon": "/fullpathto/methpub_obj.gif"
            },
            {
              "description": "method",
              "label": {"offset": 200,"length": 4},
              "icon": "/fullpathto/methpub_obj.gif"
            }
          ]
        }
      ]
    }
}
```

The description of the nodes describes to which category a node belongs to.
The icon attribute is optional. If the list of children is empty, the JSON
attribute should be omitted.


Code Completion Products
------------------------

Code completion is mandatory in many modern IDEs. A code completion server can
be very sophisticated. It can use type information or even machine learning to
figure out which completions are relevant for the user.

Conversely the protocol for sending code completions with Monto is pretty
simple. A code completion proposal consists of

 * the text of the proposal (`replacement`),
 * an insertion offset where the replacement is inserted into the source
   document (`insertionOffset`),
 * a description that is displayed to the user
 * and an icon that represents the type of the proposal.

The following image shows a triggered code completion in a java document.

![Code Completion](https://bitbucket.org/inkytonik/monto/raw/default/wiki/codecompletion_product.png)

The version message for the example looks like this:

```json
{
  "source": "HelloWorld.java",
  "product": "completions",
  "language": "json",
  "contents":
    [
       {
          "insertionOffset":319,
          "icon":"fullpathto/methpub_obj.gif",
          "description":"method: sayHelloWorld",
          "replacement":"HelloWorld"
       },
       {
          "insertionOffset":319,
          "icon":"fullpathto/methpub_obj.gif",
          "description":"method: sayYourName",
          "replacement":"YourName"
       }
    ]
}
```
