import pytest
try:
    from hypothesis import given, strategies as st, settings, example
except ImportError:
    pytest.skip("hypothesis required")
import os
from rpython.rlib.rbigint import rbigint
from pypy.module._io.interp_bytesio import W_BytesIO
from pypy.module._io.interp_textio import (W_TextIOWrapper, DecodeBuffer,
        W_IncrementalNewlineDecoder, PositionCookie,
        SEEN_CR, SEEN_LF)

# workaround suggestion for slowness by David McIver:
# force hypothesis to initialize some lazy stuff
# (which takes a lot of time, which trips the timer otherwise)
st.text().example()

def translate_newlines(text):
    text = text.replace(u'\r\n', u'\n')
    text = text.replace(u'\r', u'\n')
    return text.replace(u'\n', os.linesep)

@st.composite
def st_readline(
        draw,
        st_nlines=st.integers(min_value=0, max_value=10),
        characters=st.characters(blacklist_characters=u'\r\n')):
    n_lines = draw(st_nlines)
    fragments = []
    limits = []
    for _ in range(n_lines):
        line = draw(st.text(characters))
        fragments.append(line)
        ending = draw(st.sampled_from([u'\n', u'\r', u'\r\n']))
        fragments.append(ending)
        limit = draw(st.integers(min_value=0, max_value=len(line) + 5))
        limits.append(limit)
        limits.append(-1)
    return (u''.join(fragments), limits)

def test_newlines_bug(space):
    import _io
    w_stream = W_BytesIO(space)
    w_stream.descr_init(space, space.newbytes(b"a\nb\nc\r"))
    w_textio = W_TextIOWrapper(space)
    w_textio.descr_init(
        space, w_stream,
        encoding='utf-8', w_errors=space.newtext('surrogatepass'),
        w_newline=None)
    w_textio.read_w(space)
    assert w_textio.w_decoder.seennl == SEEN_LF | SEEN_CR

@given(data=st_readline(),
       mode=st.sampled_from(['\r', '\n', '\r\n', '']))
@settings(deadline=None, database=None)
@example(data=(u'\n\r\n', [0, -1, 2, -1, 0, -1]), mode='\r')
def test_readline(space, data, mode):
    txt, limits = data
    w_stream = W_BytesIO(space)
    w_stream.descr_init(space, space.newbytes(txt.encode('utf-8')))
    w_textio = W_TextIOWrapper(space)
    w_textio.descr_init(
        space, w_stream,
        encoding='utf-8', w_errors=space.newtext('surrogatepass'),
        w_newline=space.newtext(mode))
    lines = []
    for limit in limits:
        w_line = w_textio.readline_w(space, space.newint(limit))
        line = space.utf8_w(w_line).decode('utf-8')
        if limit >= 0:
            assert len(line) <= limit
        if line:
            lines.append(line)
        elif limit:
            break
    assert txt.startswith(u''.join(lines))

@given(data=st_readline())
@settings(deadline=None, database=None)
@example(data=(u'\n\r\n', [0, -1, 2, -1, 0, -1]))
def test_readline_none(space, data):
    txt, limits = data
    w_stream = W_BytesIO(space)
    w_stream.descr_init(space, space.newbytes(txt.encode('utf-8')))
    w_textio = W_TextIOWrapper(space)
    w_textio.descr_init(
        space, w_stream,
        encoding='utf-8', w_errors=space.newtext('surrogatepass'),
        w_newline=space.w_None)
    lines = []
    for limit in limits:
        w_line = w_textio.readline_w(space, space.newint(limit))
        line = space.utf8_w(w_line).decode('utf-8')
        if limit >= 0:
            assert len(line) <= limit
        if line:
            lines.append(line)
        elif limit:
            break
    output = txt.replace("\r\n", "\n").replace("\r", "\n")

    assert output.startswith(u''.join(lines))
@given(data=st_readline())
@settings(deadline=None, database=None)
@example(data=(u'\n\r\n', [0, -1, 2, -1, 0, -1]))
def test_incremental_decoder(space, data):
    txt, limits = data
    w_dec = W_IncrementalNewlineDecoder(space)
    w_dec.descr_init(space, space.w_None, 1)
    w_txt = space.newutf8(txt.encode("utf-8"), len(txt))
    w_res = w_dec.decode_w(space, w_txt, True)
    line = space.utf8_w(w_res).decode('utf-8')
    output = txt.replace(u"\r\n", u"\n").replace(u"\r", u"\n")
    assert line == output

    w_dec.descr_init(space, space.w_None, 0)
    w_txt = space.newutf8(txt.encode("utf-8"), len(txt))
    w_res = w_dec.decode_w(space, w_txt, True)
    line = space.utf8_w(w_res).decode('utf-8')
    assert line == txt

@given(st.text())
def test_read_buffer(text):
    buf = DecodeBuffer(text.encode('utf8'), len(text))
    chars, size = buf.get_chars(-1)
    assert chars.decode('utf8') == text
    assert len(text) == size
    assert buf.exhausted()

@given(st.text(), st.lists(st.integers(min_value=0)))
@example(u'\x80', [1])
def test_readn_buffer(text, sizes):
    buf = DecodeBuffer(text.encode('utf8'), len(text))
    strings = []
    for n in sizes:
        chars, size = buf.get_chars(n)
        s = chars.decode('utf8')
        assert size == len(s)
        if not buf.exhausted():
            assert len(s) == n
        else:
            assert len(s) <= n
        strings.append(s)
    assert ''.join(strings) == text[:sum(sizes)]

@given(content=st_readline(characters=st.characters(blacklist_categories='C')))
def test_tell(space, content):
    txt, limits = content

    restxt = translate_newlines(txt)
    resstr = restxt.encode('utf-8')
    for read_chars_before_seeking in range(len(restxt)):
        w_stream = W_BytesIO(space)
        w_stream.descr_init(space, space.newbytes(txt.encode('utf-8')))

        w_textio = W_TextIOWrapper(space)
        w_textio.descr_init(
            space, w_stream,
            encoding='utf-8'
        )

        w_res1 = w_textio.read_w(space, space.newint(read_chars_before_seeking))
        assert space.len_w(w_res1) <= read_chars_before_seeking
        w_tell = w_textio.tell_w(space)
        w_textio.seek_w(space, space.newint(0)) # seek to beginning
        w_textio.seek_w(space, w_tell) # then back to position
        w_res2 = w_textio.read_w(space)
        w_res = space.add(w_res1, w_res2)
        res = space.text_w(w_res)
        assert res == resstr

@given(content=st_readline(characters=st.characters(blacklist_categories='C')))
def test_getstate_setstate(space, content):
    txt, limits = content

    restxt = translate_newlines(txt)
    for read_chars_before_getstate in range(len(restxt)):
        w_stream = W_BytesIO(space)
        w_stream.descr_init(space, space.newbytes(txt.encode('utf-8')))

        w_textio = W_TextIOWrapper(space)
        w_textio.descr_init(
            space, w_stream,
            encoding='utf-8'
        )
        w_state_start = w_textio.w_decoder.getstate_w(space)
        w_res1 = w_textio.read_w(space, space.newint(read_chars_before_getstate))
        w_current_state = w_textio.w_decoder.getstate_w(space)
        w_textio.w_decoder.setstate_w(space, w_state_start)
        w_textio.w_decoder.setstate_w(space, w_current_state)
        w_res2 = w_textio.read_w(space)
        w_res = space.add(w_res1, w_res2)
        res = space.text_w(w_res).decode("utf-8")
        assert res == restxt

def test_cookie(space):
    val1 = eval("0x" + "1" * 128)
    cookie1 = PositionCookie(rbigint.fromlong(val1))
    val2 = cookie1.pack()
    cookie = PositionCookie(val2)
    assert cookie.start_pos > 0
    assert cookie.dec_flags > 0
    assert cookie.bytes_to_feed > 0
    assert cookie.chars_to_skip > 0
    assert cookie.need_eof > 0
    assert cookie.start_pos == cookie.start_pos
    assert cookie.dec_flags == cookie.dec_flags
    assert cookie.bytes_to_feed == cookie.bytes_to_feed
    assert cookie.chars_to_skip == cookie.chars_to_skip
    assert cookie.need_eof == cookie.need_eof
