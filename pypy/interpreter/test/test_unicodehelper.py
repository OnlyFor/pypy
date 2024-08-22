# encoding: utf-8
import pytest

from pypy.interpreter.unicodehelper import (
    utf8_encode_utf_8, decode_utf8sp,
)

from pypy.interpreter.unicodehelper import str_decode_utf8, utf8_encode_latin_1
from pypy.interpreter.unicodehelper import utf8_encode_ascii, str_decode_ascii
from pypy.interpreter.unicodehelper import str_decode_unicode_escape
from pypy.interpreter.unicodehelper import str_decode_raw_unicode_escape
from pypy.interpreter.unicodehelper import utf8_encode_utf_16_le
from pypy.interpreter.unicodehelper import utf8_encode_utf_32_le
from pypy.interpreter import unicodehelper as uh
from pypy.module._codecs.interp_codecs import CodecState

class Hit(Exception):
    pass

class FakeSpace:
    def __init__(self, space):
        self.space = space
    def __getattr__(self, name):
        if name in ('w_UnicodeEncodeError', 'w_UnicodeDecodeError'):
            raise Hit
        raise AttributeError(name)
    def newbytes(self, s):
        return s
    def newtext(self, s):
        return self.space.newtext(s)

def test_encode_utf_8_combine_surrogates(space):
    """
    In the case of a surrogate pair, the error handler should
    called with a start and stop position of the full surrogate
    pair (new behavior in python3.6)
    """
    #               /--surrogate pair--\
    #    \udc80      \ud800      \udfff
    b = "\xed\xb2\x80\xed\xa0\x80\xed\xbf\xbf"
    _space = FakeSpace(space)

    calls = []

    def errorhandler(errors, encoding, msg, w_s, start, end):
        """
        This handler will be called twice, so asserting both times:

        1. the first time, 0xDC80 will be handled as a single surrogate,
           since it is a standalone character and an invalid surrogate.
        2. the second time, the characters will be 0xD800 and 0xDFFF, since
           that is a valid surrogate pair.
        """
        s = w_s._utf8
        calls.append(s.decode("utf-8")[start:end])
        return 'abc', end, 'b', s, w_s
    w_b = space.newtext(b)
    res = utf8_encode_utf_8(
        space, b, w_b, 'strict',
        errorhandler=errorhandler,
        allow_surrogates=False
    )
    assert res == "abcabc"
    assert calls == [u'\udc80', u'\uD800\uDFFF']

#def test_bad_error_handler():
    # replaced by the test test_repeated_pos_return
    # in test_codecs. following CPython's approach

def test_decode_utf8sp():
    space = FakeSpace(None)
    assert decode_utf8sp(space, "\xed\xa0\x80") == ("\xed\xa0\x80", 1, 3)
    assert decode_utf8sp(space, "\xed\xb0\x80") == ("\xed\xb0\x80", 1, 3)
    got = decode_utf8sp(space, "\xed\xa0\x80\xed\xb0\x80")
    assert map(ord, got[0].decode('utf8')) == [0xd800, 0xdc00]
    got = decode_utf8sp(space, "\xf0\x90\x80\x80")
    assert map(ord, got[0].decode('utf8')) == [0x10000]


def test_utf8_encode_latin1_ascii_prefix():
    space = FakeSpace(None)
    utf8 = b'abcde\xc3\xa4g'
    b = utf8_encode_latin_1(space, utf8, utf8, None, None)
    assert b == b'abcde\xe4g'

def test_latin1_shortcut_bug(space):
    state = space.fromcache(CodecState)
    handler = state.encode_error_handler

    sin = u"a\xac\u1234\u20ac\u8000"
    sin_utf8 = sin.encode("utf-8")
    assert utf8_encode_latin_1(space, sin_utf8, space.newtext(sin_utf8), "backslashreplace", handler) == sin.encode("latin-1", "backslashreplace")

def test_unicode_escape_incremental_bug(space):
    class FakeUnicodeDataHandler:
        def call(self, name):
            assert name == "QUESTION MARK"
            return ord("?")
    unicodedata_handler = FakeUnicodeDataHandler()
    input = u"äҰ𐀂?"
    data = b'\\xe4\\u04b0\\U00010002\\N{QUESTION MARK}'
    for i in range(1, len(data)):
        s = data[:i]
        w_s = space.newtext(s)
        result1, _, lgt1, _ = str_decode_unicode_escape(space, s, w_s, 'strict', False, None, unicodedata_handler)
        s1 = data[lgt1:i] + data[i:]
        w_s1 = space.newtext(s1)
        result2, _, lgt2, _ = str_decode_unicode_escape(space, s1, w_s1, 'strict', True, None, unicodedata_handler)
        assert lgt1 + lgt2 == len(data)
        assert input == (result1 + result2).decode("utf-8")

def test_raw_unicode_escape_incremental_bug(space):
    input = u"xҰa𐀂"
    data = b'x\\u04b0a\\U00010002'
    for i in range(1, len(data)):
        s = data[:i]
        w_s = space.newtext(s)
        result1, _, lgt1 = str_decode_raw_unicode_escape(space, s, w_s, 'strict', False, None)
        s = data[lgt1:i] + data[i:]
        w_s = space.newtext(s)
        result2, _, lgt2 = str_decode_raw_unicode_escape(space, s, w_s, 'strict', True, None)
        assert lgt1 + lgt2 == len(data)
        assert input == (result1 + result2).decode("utf-8")

def test_raw_unicode_escape_backslash_without_escape():
    data = b'[:/?#[\\]@]\\'
    space = FakeSpace(None)
    result, _, l = str_decode_raw_unicode_escape(space, data, data, 'strict', True, None)
    assert l == len(data)
    assert result == data

def test_raw_unicode_escape_bug_escape_backslash():
    data = b'\\\\'
    space = FakeSpace(None)
    res = str_decode_raw_unicode_escape(space, data, data, 'strict', True, None)
    assert res[0] == '\\\\'

    data = b'\\\xef'
    res = str_decode_raw_unicode_escape(space, data, data, 'strict', True, None)
    assert res[0].decode("utf-8") == u'\\\xef'

def test_utf16_encode_bytes_replacement_is_simply_copied():
    space = FakeSpace(None)
    def errorhandler(errors, encoding, msg, s, start, end):
        return 'abcd', end, 'b', s, s

    s = b'[\xed\xb2\x80]'
    res = utf8_encode_utf_16_le(
        space, s, s, 'strict',
        errorhandler=errorhandler,
        allow_surrogates=False
    )
    assert res == "[\x00abcd]\x00"


def test_utf32_encode_bytes_replacement_is_simply_copied(space):
    _space = FakeSpace(space)
    s = b'[\xed\xb2\x80]'
    def errorhandler(errors, encoding, msg, w_s, start, end):
        return 'abcd', end, 'b', s, w_s

    res = utf8_encode_utf_32_le(
        _space, s, space.newtext(s), 'strict',
        errorhandler=errorhandler,
        allow_surrogates=False
    )
    assert res == "[\x00\x00\x00abcd]\x00\x00\x00"

