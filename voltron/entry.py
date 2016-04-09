"""
This is the main entry point for Voltron from the debugger host's perspective.
This file is loaded into the debugger through whatever means the given host
supports.

LLDB:

    (lldb) command script import /path/to/voltron/entry.py

GDB:

    (gdb) source /path/to/voltron/entry.py

VDB:

    (vdb) script /path/to/voltron/entry.py

WinDbg/CDB (via PyKD):

    > .load pykd.pyd
    > !py --global C:\path\to\voltron\entry.py
"""

log = None

try:
    import logging
    import os
    import sys
    blessed = None
    import blessed

    # add vtrace to the path so that dbg_vdb.py can import from vdb/vtrace.
    if "vtrace" in locals():
        def parent_directory(the_path):
            return os.path.abspath(os.path.join(the_path, os.pardir))

        def add_vdb_to_path(vtrace):
            sys.path.append(parent_directory(parent_directory(vtrace.__file__)))

        add_vdb_to_path(vtrace)
    else:
        pass

    import voltron
    from voltron.plugin import pm
    from voltron.core import Server

    log = voltron.setup_logging('debugger')

    # figure out in which debugger host we are running
    args = []
    try:
        import lldb
        host = "lldb"
    except ImportError:
        pass
    try:
        import gdb
        host = "gdb"
    except ImportError:
        pass
    try:
        import pykd
        host = "windbg"
    except:
        pass
    if "vtrace" in locals():
        host = "vdb"
        args = [db]
    if not host:
        raise Exception("No debugger host is present")

    # register any plugins that were loaded
    pm.register_plugins()

    # get the debugger plugin for the host we're in
    plugin = pm.debugger_plugin_for_host(host)

    # set up command and adaptor instances
    voltron.debugger = plugin.adaptor_class(*args)
    voltron.command = plugin.command_class(*args)

    # create and start the voltron server
    voltron.server = Server()
    if host != "gdb":
        voltron.server.start()

    print(blessed.Terminal().bold_red("Voltron loaded."))
    if host == 'lldb':
        print("Run `voltron init` after you load a target.")

except Exception as e:
    import traceback
    msg = "An error occurred while loading Voltron:\n\n{}".format(traceback.format_exc())
    if blessed:
        msg = blessed.Terminal().bold_red(msg)
    if log:
        log.exception("Exception raised while loading Voltron")
    print(msg)
