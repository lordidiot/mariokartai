import numpy as np
from dataclasses import dataclass

"""
enum jg_pixfmt {
    JG_PIXFMT_XRGB8888, /**< 32-bit pixels with bits 24-31 unused, bits 16-23
                            for Red, bits 8-15 for Green, and bits 0-7 for
                            Blue */
    JG_PIXFMT_XBGR8888, /**< 32-bit pixels with bits 24-31 unused, bits 16-23
                            for Blue, bits 8-15 for Green, and bits 0-7 for
                            Red */
    JG_PIXFMT_RGBX5551, /**< 16-bit pixels with bits 11-15 for Red, bits 6-10
                            for Green, bits 1-5 for Blue, and bit 0 unused */
    JG_PIXFMT_RGB565    /**< 16-bit pixels with bits 11-15 for Red, bits 5-10 
                            for Green, and bits 0-4 for Blue */
};
"""

@dataclass
class FrameData:
    pixfmt: int
    w: int
    h: int
    x: int
    y: int
    nbytes: int

pixfmt_to_bpp = {
    0: 32,
    1: 32,
    2: 16,
    3: 16
}

pixfmt_to_scale = {
    0: 255,
    1: 255,
    2: 31,    
    3: (31, 63, 31),
}

pixfmt_to_mask_and_shift = {
    0: ((0xff0000, 16), (0x00ff00, 8), (0x0000ff, 0)),
    1: ((0x0000ff, 0), (0x00ff00, 8), (0xff0000, 16)),
    2: ((0xf800, 11), (0x07c0, 6), (0x003e, 1)),
    3: ((0xf800, 11), (0x07e0, 5), (0x001f, 0))
}

def frame_to_rgb(frame_data: FrameData, buffer) -> np.ndarray:
    bytespp = pixfmt_to_bpp[frame_data.pixfmt] // 8
    mask_and_shift = pixfmt_to_mask_and_shift[frame_data.pixfmt]
    scale = pixfmt_to_scale[frame_data.pixfmt]
    w, h = frame_data.w + frame_data.x, frame_data.h + frame_data.y
    assert frame_data.nbytes == w * h * bytespp, "Invalid nbytes"
    assert len(buffer) >= frame_data.nbytes, "Buffer size too small"
    buffer = buffer[:frame_data.nbytes]

    vals = np.frombuffer(buffer, dtype=np.uint16).reshape(h, w)
    pixels = np.stack(list((vals & mask) >> shift for mask, shift in mask_and_shift), axis=-1)
    pixels = pixels / np.array(scale)
    return pixels
