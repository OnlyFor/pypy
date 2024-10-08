.. _jit-hooks:

JIT hooks
=========

There are several hooks in the ``pypyjit`` module that may help you with
understanding what pypy's JIT is doing while running your program:

.. function:: dont_trace_here(next_instr, is_being_profiled, pycode)
    
.. function:: get_jitcell_at_key(next_instr, is_being_profiled, pycode)
    
.. function:: get_stats_asmmemmgr()

    Returns the raw memory currently used by the JIT backend,
    as a pair (total_memory_allocated, memory_in_use).
    
.. function:: residual_call(callable, *args, **keywords)

    For testing.  Invokes callable(...), but without letting
    the JIT follow the call.
 
.. function:: set_compile_hook(callable, operations=True)

    Set a compiling hook that will be called each time a loop is compiled.

    The callable will be called with the ``pypyjit.JitLoopInfo`` object.
    Refer to it's documentation for details.

    Note that jit hook is not reentrant. It means that if the code
    inside the jit hook is itself jitted, it will get compiled, but the
    jit hook won't be called for that.

    if operations=False, no list of operations will be available. Useful
    if the hook is supposed to be very lightweight.

.. function:: set_abort_hook(hook)

    Set a hook (callable) that will be called each time there is tracing
    aborted due to some reason.

    The hook will be invoked with the siagnture:
    ``hook(jitdriver_name, greenkey, reason, oplist)``

    Reason is a string, the meaning of other arguments is the same
    as attributes on JitLoopInfo object

.. function:: set_trace_too_long_hook(hook)
        
    Set a hook (callable) that will be called each time we abort
    tracing because the trace is too long.
    
    The hook will be called with the signature:
    ``hook(jitdriver_name, greenkey)``
 

.. function:: enable_debug()

    Start recording debugging counters for ``get_stats_snapshot``

    Currently disabled.

.. function:: disable_debug()

    Stop recording debugging counters for ``get_stats_snapshot``

    Currently disabled.

.. function:: get_stats_snapshot()

    Get the jit status in the specific moment in time. Note that this
    is eager - the attribute access is not lazy, if you need new stats
    you need to call this function again. You might want to call
    ``enable_debug`` to get more information. It returns an instance
    of ``JitInfoSnapshot``

.. class:: JitInfoSnapshot

    A class describing current snapshot. Usable attributes:

    * ``counters`` - internal JIT integer counters

    * ``counter_times`` - internal JIT float counters, notably time spent
      TRACING and in the JIT BACKEND

    * ``loop_run_times`` - counters for number of times loops are run, only
      works when ``enable_debug`` is called.

.. class:: JitLoopInfo

   A class containing information about the compiled loop. Usable attributes:

   * ``operations`` - list of operations, if requested

   * ``jitdriver_name`` - the name of jitdriver associated with this loop

   * ``greenkey`` - a key at which the loop got compiled (e.g. code position,
     is_being_profiled, pycode tuple for python jitdriver)

   * ``loop_no`` - loop cardinal number

   * ``bridge_no`` - id of the fail descr

   * ``type`` - "entry bridge", "loop" or "bridge"

   * ``asmaddr`` - an address in raw memory where assembler resides

   * ``asmlen`` - length of raw memory with assembler associated

Resetting the JIT
=================

.. function:: releaseall()

   Marks all current machine code objects as ready to release. They will be
   released at the next GC (unless they are currently in use in the stack of
   one of the threads).  Doing ``pypyjit.releaseall(); gc.collect()`` is a
   heavy hammer that forces the JIT roughly back to the state of a newly
   started PyPy.

.. function:: set_param(*args, **keywords)

    Configure the tunable JIT parameters, parameter names are listed in :ref:`Jit Help<jit-help>` :

    * ``set_param(name=value, ...)`` as keyword arguments

    * ``set_param("name=value,name=value")`` as a user-supplied string

    * ``set_param("off")`` disable the jit

    * ``set_param("default")`` restore all defaults
   
