import py
from rpython.rtyper.lltypesystem import lltype, llmemory, rffi, rstr
from rpython.translator import cdir
from rpython.translator.tool.cbuild import ExternalCompilationInfo


cwd = py.path.local(__file__).dirpath()
rvmp = cwd.join('../../..')
rvmp = rvmp.join('rpython/rlib/rvmprof/src')

eci = ExternalCompilationInfo(
    includes=[cwd.join('faulthandler.h')],
    include_dirs=[str(cwd), cdir, rvmp],
    separate_module_files=[cwd.join('faulthandler.c')],
    compile_extra=['-DRPYTHON_VMPROF=1'])

eci_later = eci.merge(ExternalCompilationInfo(
    pre_include_bits=['#define PYPY_FAULTHANDLER_LATER\n']))
eci_user = eci.merge(ExternalCompilationInfo(
    pre_include_bits=['#define PYPY_FAULTHANDLER_USER\n']))

def direct_llexternal(*args, **kwargs):
    kwargs.setdefault('_nowrapper', True)
    kwargs.setdefault('compilation_info', eci)
    return rffi.llexternal(*args, **kwargs)


DUMP_CALLBACK = lltype.Ptr(lltype.FuncType(
                     [rffi.INT_real, rffi.VOIDP, rffi.INT_real], lltype.Void))

pypy_faulthandler_setup = direct_llexternal(
    'pypy_faulthandler_setup', [DUMP_CALLBACK], rffi.CCHARP)

pypy_faulthandler_teardown = direct_llexternal(
    'pypy_faulthandler_teardown', [], lltype.Void)

pypy_faulthandler_enable = direct_llexternal(
    'pypy_faulthandler_enable', [rffi.INT_real, rffi.INT_real], rffi.CCHARP)

pypy_faulthandler_disable = direct_llexternal(
    'pypy_faulthandler_disable', [], lltype.Void)

pypy_faulthandler_is_enabled = direct_llexternal(
    'pypy_faulthandler_is_enabled', [], rffi.INT)

pypy_faulthandler_write = direct_llexternal(
    'pypy_faulthandler_write', [rffi.INT_real, rffi.CCHARP], lltype.Void)

pypy_faulthandler_write_uint = direct_llexternal(
    'pypy_faulthandler_write_uint', [rffi.INT_real, lltype.Unsigned, rffi.INT],
                                    lltype.Void)

pypy_faulthandler_dump_traceback = direct_llexternal(
    'pypy_faulthandler_dump_traceback',
    [rffi.INT_real, rffi.INT_real, llmemory.Address], lltype.Void)

pypy_faulthandler_dump_traceback_later = direct_llexternal(
    'pypy_faulthandler_dump_traceback_later',
    [rffi.LONGLONG, rffi.INT, rffi.INT_real, rffi.INT], rffi.CCHARP,
    compilation_info=eci_later)

pypy_faulthandler_cancel_dump_traceback_later = direct_llexternal(
    'pypy_faulthandler_cancel_dump_traceback_later', [], lltype.Void)

pypy_faulthandler_check_signum = direct_llexternal(
    'pypy_faulthandler_check_signum',
    [rffi.LONG], rffi.INT,
    compilation_info=eci_user)

pypy_faulthandler_register = direct_llexternal(
    'pypy_faulthandler_register',
    [rffi.INT_real, rffi.INT_real, rffi.INT_real, rffi.INT_real], rffi.CCHARP,
    compilation_info=eci_user)

pypy_faulthandler_unregister = direct_llexternal(
    'pypy_faulthandler_unregister',
    [rffi.INT], rffi.INT,
    compilation_info=eci_user)


# for tests...

pypy_faulthandler_read_null = direct_llexternal(
    'pypy_faulthandler_read_null', [], lltype.Void)

pypy_faulthandler_read_null_releasegil = direct_llexternal(
    'pypy_faulthandler_read_null', [], lltype.Void,
    _nowrapper=False, releasegil=True)

pypy_faulthandler_sigsegv = direct_llexternal(
    'pypy_faulthandler_sigsegv', [], lltype.Void)

pypy_faulthandler_sigsegv_releasegil = direct_llexternal(
    'pypy_faulthandler_sigsegv', [], lltype.Void,
    _nowrapper=False, releasegil=True)

pypy_faulthandler_sigfpe = direct_llexternal(
    'pypy_faulthandler_sigfpe', [], lltype.Void)

pypy_faulthandler_sigabrt = direct_llexternal(
    'pypy_faulthandler_sigabrt', [], lltype.Void)

pypy_faulthandler_stackoverflow = direct_llexternal(
    'pypy_faulthandler_stackoverflow', [lltype.Float], lltype.Float)
