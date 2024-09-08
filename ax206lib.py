import usb1
from werkzeug.utils import secure_filename
import os
import base64
from io import BytesIO
from PIL import Image
import logging

BRIGHTNESS_MIN = 0
BRIGHTNESS_MAX = 8
BRIGHTNESS_DEFAULT = 6

CURRENT_BRIGHTNESS = BRIGHTNESS_DEFAULT

def set_brightness_byval(value):
    CURRENT_BRIGHTNESS = value
    with usb1.USBContext() as context:
        handle = context.openByVendorIDAndProductID(
            0x1908,
            0x0102,
            skip_on_error=True,
        )
        if handle is None:
            logging.critical("Handle not is none -- check if device is plugged in.")
        with handle.claimInterface(0x00):
            logging.info("Handle claimed.")

            width, height = get_dimensions(handle)
            set_brightness(handle, value)

def send_base64_image(data):
    image_bytes = base64.b64decode(data)
    im = Image.open(BytesIO(image_bytes)).convert('RGB')
    with usb1.USBContext() as context:
        handle = context.openByVendorIDAndProductID(
            0x1908,
            0x0102,
            skip_on_error=True,
        )
        if handle is None:
            logging.critical("Handle not is none -- check if device is plugged in.")
        with handle.claimInterface(0x00):
            logging.info("Handle claimed.")

            width, height = get_dimensions(handle)
            #set_brightness(handle, CURRENT_BRIGHTNESS)

            logging.info("DONE")

            if im is not None:
                draw_pil_image(handle, im, 0, 0, width, height)  # portrait mode - usb plug faces downward

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_color16(rgb_arr):
    """
    conversion code lifted from the manufacturer
    alpha is discarded if present
    """
    R = rgb_arr[0]
    G = rgb_arr[1]
    B = rgb_arr[2]
    num = 0
    num2 = 0

    num = (num | (R >> 3))
    num2 = (num2 | (num << 11))

    num = 0
    num = (num | (G >> 2))
    num2 = (num2 | (num << 5))

    num = 0
    num = (num | (B >> 3))
    num2 = (num2 | num)

    return num2

def trim_bits(int_input):
    return_num = int_input
    while return_num >= 256:
        return_num = (return_num >> 1)
    logging.info("RET: " + return_num)
    return return_num

def write_barray(handle, input_array):
    my_bytes = bytearray()
    if type(input_array) == bytearray:
        my_bytes = input_array
    else:
        my_bytes = bytearray(input_array)
    handle.bulkWrite(0x01, my_bytes, timeout=5000)
    pass

#def read_buffer(handle, address, length, timeout=3000):
#    a = handle.bulkRead(address, length, timeout=timeout)
#    return a

def get_dimensions(handle):
    write_barray(handle, [
        0x55, 0x53, 0x42, 0x43, 0xde, 0xad, 0xbe, 0xef,
        0x5, (0x5 >> 8), (0x5 >> 16), (0x5 >> 24), 0x00, 0x00, 0x10,
        0xcd, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ])

    a = handle.bulkRead(0x81, 5)
    #print(a)
    #print("---")
    logging.debug(f"Get dimensions raw return: {a}")
    width = a[0] | (a[1] << 8)
    height = a[2] | (a[3] << 8)
    #for x in a:
    #    print(x)
    logging.info("Width: {width}")
    logging.info("Height: {height}")
    do_ack(handle)
    return width, height

def do_ack(handle):
    ack = handle.bulkRead(0x81, 13, timeout=3000)
    #print(ack)
    logging.debug(f"ACK raw return: {ack}")

def set_brightness(handle, user_brightness_val):
    """
    brightness_val must be between 0 and 8.
    7 is default
    """
    brightness_val = BRIGHTNESS_DEFAULT
    if user_brightness_val >=0 and user_brightness_val <= 8:
        brightness_val = user_brightness_val
    elif user_brightness_val < 0:
        brightness_val = 0
    elif user_brightness_val > 8:
        brightness_val = 8
    write_barray(handle, [
        0x55, 0x53, 0x42, 0x43, 0xde, 0xad, 0xbe, 0xef,
        0x0, (0x0 >> 8), (0x0 >> 16), (0x8 >> 24), 0x00, 0x00, 0x10,
        0xcd, 0, 0, 0, 0, 6, 0x01, 0x01, 0x00, brightness_val, brightness_val >> 8, 0, 0, 0, 0, 0
    ])
    do_ack(handle)
    pass

def init_blit(handle, r0, r1, r2, r3):
    block_len = (r2-r0)*(r3-r1) * 2
    logging.info("Block LEN; {block_len}")
    block1 = (block_len & (0xFF-1))
    block2 = (block_len & (0x10000-1)) >> 8
    block3 = (block_len & (0x1000000-1)) >> 16
    block4 = (block_len & (0x100000000-1)) >> 24
    write_barray(handle, [
        0x55, 0x53, 0x42, 0x43, 0xde, 0xad, 0xbe, 0xef,
        block1, block2, block3, block4, 0x00, 0x00, 0x10,
        0xcd, 0, 0, 0, 0, 6, 0x12,
        (r0 & (0xFF)), ((r0 & (0x10000-1)) >> 8), (r1 & (0xFF)), (r1 & (0x10000-1) >> 8),
        ((r2-1) & (0xFF)), (((r2-1) & (0x10000-1)) >> 8), ((r3-1) & (0xFF)), (((r3-1) & (0x10000-1)) >> 8), 0
    ])

def draw_pil_image(handle, pil_im_obj, r0, r1, r2, r3):
    init_blit(handle, r0, r1, r2, r3)
    assert type(pil_im_obj) == Image.Image
    my_bytes_2 = bytearray()
    im1 = Image.Image.getdata(pil_im_obj)
    for x in im1:
        h565 = get_color16([x[0], x[1], x[2]])
        b1 = (int(h565 & 0xFF))
        b2 = (int((h565 & 0xFF00)) >> 8)
        logging.debug(f"Blit {h565} TO -> {b1}, {b2}")
        my_bytes_2.append(b2)
        my_bytes_2.append(b1)

    logging.info(f"Blit buffer len: {len(my_bytes_2)}")
    sent_bytes = handle.bulkWrite(0x01, my_bytes_2, timeout=5000)
    logging.info(f"Blit sent bytes: {sent_bytes}")
    do_ack(handle)
