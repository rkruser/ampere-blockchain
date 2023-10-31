"""
For parsing and creating binary data of all different protocol versions.

To be used for app messaging and blockchain blocks.

Idea:
- config folders contain specifications for all the different data formats and versions
- create parser objects for all these different specs
(make use of struct pack and struct unpack, etc.)


Conventions and hardcodings:
- Everything is big-endian (network convention)
- First two bytes of anything specify version
- Config convention: fixed-length fields should precede variable-length fields (though this is not strictly necessary)
- All lower-case types are hardcoded (like uint, string, variable_string_256, etc.)
- Upper-case types too?
- Everything base-64 encoded before sending? Or...
- All messages logged (base 64 encode for log purposes, at least)

Steps:
 - Iterate through config directory and get all config files
 - Construct parser objects for each config and store them mapped to type and version in a dict (have a class maintaining this)
 - When reading messages, first extract version from first two bytes, then use correct parser for outer message
 - Outer message parser can detect versions of inner data and use correct inner parsers on the fly
 - When writing messages, versions should default to latest version of protocol/data type/etc. Save latest version upon reading configs
 - Need classes/functions to support writing as well as reading
 - Have a "latest" class that always uses the latest version of protocols?


def read_configs():
    # should walk through the config directory and read in all yaml files
    # use the os.path.walk feature
    # Call make_parser for each

def make_parser(config_file_contents):
    # should parse the contents as yaml, then create object/function that can parse the type
    # Store type, version, struct format strings, etc. in object
    # Register function before returning it
    # Return function that takes bytestring and returns parsed object with param keys set


PARSERS.make_message(type, headers, data)
PARSERS.read_message(message)

Message nodes have "header" and "data" version fields?

INNER_MESSAGE should be less complicated, multiple types, and header fields dependent on type

Messaging procedure:
- Log all incoming messages (record send timestamp and received timestamp)
- Pass all messages to a node monitor that tracks node metadata to look for suspicious or incorrect activity
    (e.g., look for discrepancies between send and receive timestamps, replay attacks, etc.)
- Verify all signatures and that they match the claimed sender and/or follow protocol
- Place all verified incoming messages into appropriate queue depending on type and purpose
- Queues are organized so that they can be done in parallel, but within a queue things are serialized
- e.g., if a particular message exchange has state, complete the exchange before moving on?

Nodes subscribe to receive messages about updates for particular patients


Question:
- Should we just put the version info in the type strings themselves? For easy hashing?


"""