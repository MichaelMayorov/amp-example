AMP
===

Links
*****
 * http://amp-protocol.net/
 * http://amp-protocol.net/Types
 * http://twistedmatrix.com/documents/13.0.0/core/howto/amp.html

Notation for AMP packets
========================

*".."* is a length-prefixed string.  All other basic types are collapsed to strings, as described in http://amp-protocol.net/Types. ::

   {{{
   { k:v, k:v, .. }
   }}}

is a packet, encoded as a sequence of keys and values, each with a length prefix, follwed by two 00 bytes ::

   {{{
   [v1, v2, .. ]
   }}}

is a ListOf, encoded as a sequence of values, each with a length prefix ::

   {{{
   [(k:v, k:v, ..), ..]
   }}}

is an AmpList, encoded as a sequence of keys and values, each with a length prefix.  Each list element ( .. ) is terminated by two 00 bytes

Examples
********
::

   {{{
   --> {"_ask":"34", "_command":"LookupPeople", "people":[("first":"Dustin", "last":Mitchell", "vehicle_ids":["1398", "2983"]), ("first":"Tom", "last":"Prince", "vehicle_ids":[])]}
   --> {"_ask":"13", "_command":"Product", "factors":["10", "20", "30"]}
   }}}

Notation for AMP Schema
=======================

The schema specifies what structure to expect from an AMP message so that the sender knows how to encode it, and the receiver knows how to decode it.  The types are defined in http://amp-protocol.net/Types.  We will use the Python notation for these types.  See http://twistedmatrix.com/documents/13.0.0/api/twisted.protocols.amp.html

Examples
********
::

   {{{
   [('a', amp.Integer()), ('b', amp.String())]
   [('factors', amp.ListOf(amp.Integer()))]
   [('people', amp.AmpList([
        ('first', amp.String()),
        ('last', amp.String()),
        ('vehicle_ids', amp.ListOf(amp.Integer())),
   ]))]
   }}}    

Protocol messages
=================

.. note :: 

   - **-->** for packets from master to slave
   - **<--** for packets from slave to master

Connection Setup
****************

Share slave version, available commands, etc. to the master ::

   --> {"_ask":"31", "_command":"getinfo"}
   <-- {  "_answer": 31, "commands": [("name": "cmd1", "version": 0.1), ...],  "environ": [("key": "foo", "value": "bar"), ...], "system": "OpenBSD",  "basedir": "/", "version": 1 }

Executing shell command
***********************
::

   {{{
   --> {"_ask":"34", "_command":"execute", "cmd_path":"/bin/echo", "args":["-e", "hello"], "builder":"python2.7"}
   <-- {"_answer":"34", "ret_code": 0, builder: "python2.7", stderr:"some stuff from stderr", stdout:"stuff from stdout"}
   }}}

Executing mkdir
***************
::

   {{{
   --> {"_ask":"34", "_command":"mkdir", "dir":"build/tmp", "builder":"python2.7"}
   <-- {"_answer":"34", "ret_code": "0"}
   }}}

(similar for other commands like rm)

Set builders list
*****************
::

   --> { "_ask": 32, "_command": "setBuilderList", "args": [("builder_name": "builder1", "dir": "/path/to/builder/"), ...] }
   <-- {"_answer":"32", "ret_code": 0 }

Start build
***********
::

   --> { "_ask": 30, "_command": "startBuild", "builder":"python2.7" }
   <-- {"_answer":"30", "ret_code": 0 }

Stop build
**********
::

   --> { "_ask": 30, "_command": "stopBuild", "builder":"python2.7", "why": "because" }
   <-- {"_answer":"30", "ret_code": 0 }

Log streaming
*************
::

   -->  { 'builder': 'py2.7', 'args': '-la', 'command': '/bin/ls', '_command': 'RemoteStartCommand', 'environ': '\x00\x03key\x00\x03foo\x00\x05value\x00\x03bar\x00\x00\x00\x03key\x00\x03baz\x00\x05value\x00\x04quux\x00\x00', '_ask': '4' }
   <--  { 'line': 'bla-bla-bla', '_command': 'RemoteAcceptLog' }
   <--  {'line': 'bla-bla-bla-bla', '_command': 'RemoteAcceptLog' }

