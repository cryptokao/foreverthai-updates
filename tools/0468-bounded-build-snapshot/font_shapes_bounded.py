"""Exact retained Sarabun/HarfBuzz shaping; word cuts supplied by reviewed data, no NLP/model dependency."""
import math, unicodedata
import freetype, uharfbuzz as hb
from PIL import Image, ImageChops

def initialize(fontfile):
    global face, font
    face = freetype.Face(str(fontfile))
    face.set_pixel_sizes(0, 34)
    font = hb.Font(hb.Face(fontfile.read_bytes()))
    font.scale = (34 * 64, 34 * 64)
    hb.ot_font_set_funcs(font)

def render(word):
    buf = hb.Buffer()
    buf.add_str(word)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    pen = 0
    glyphs = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        assert info.codepoint, word
        face.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER)
        glyph = face.glyph
        bm = glyph.bitmap
        x = round((pen + pos.x_offset) / 64) + glyph.bitmap_left
        y = 44 - round(pos.y_offset / 64) - glyph.bitmap_top
        if bm.width and bm.rows:
            glyphs.append((x, y, Image.frombytes("L", (bm.width, bm.rows), bytes(bm.buffer))))
        pen += pos.x_advance
    left = min([0] + [x for x,y,im in glyphs])
    right = max([math.ceil(pen / 64)] + [x + im.width for x,y,im in glyphs])
    im = Image.new("L", (right - left, 56))
    for x, y, g in glyphs:
        assert 0 <= y and y + g.height <= im.height, (word, y, g.height)
        x -= left
        area = (x,y,x+g.width,y+g.height)
        im.paste(ImageChops.lighter(im.crop(area), g), (x, y))
    return im, left, round(pen / 64, 2)
