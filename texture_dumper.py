import decima
import os
import struct
import argparse
from typing import Dict, List, Set
from enum import IntEnum


class DXGI(IntEnum):
    DXGI_FORMAT_UNKNOWN = 0,
    DXGI_FORMAT_R32G32B32A32_TYPELESS = 1,
    DXGI_FORMAT_R32G32B32A32_FLOAT = 2,
    DXGI_FORMAT_R32G32B32A32_UINT = 3,
    DXGI_FORMAT_R32G32B32A32_SINT = 4,
    DXGI_FORMAT_R32G32B32_TYPELESS = 5,
    DXGI_FORMAT_R32G32B32_FLOAT = 6,
    DXGI_FORMAT_R32G32B32_UINT = 7,
    DXGI_FORMAT_R32G32B32_SINT = 8,
    DXGI_FORMAT_R16G16B16A16_TYPELESS = 9,
    DXGI_FORMAT_R16G16B16A16_FLOAT = 10,
    DXGI_FORMAT_R16G16B16A16_UNORM = 11,
    DXGI_FORMAT_R16G16B16A16_UINT = 12,
    DXGI_FORMAT_R16G16B16A16_SNORM = 13,
    DXGI_FORMAT_R16G16B16A16_SINT = 14,
    DXGI_FORMAT_R32G32_TYPELESS = 15,
    DXGI_FORMAT_R32G32_FLOAT = 16,
    DXGI_FORMAT_R32G32_UINT = 17,
    DXGI_FORMAT_R32G32_SINT = 18,
    DXGI_FORMAT_R32G8X24_TYPELESS = 19,
    DXGI_FORMAT_D32_FLOAT_S8X24_UINT = 20,
    DXGI_FORMAT_R32_FLOAT_X8X24_TYPELESS = 21,
    DXGI_FORMAT_X32_TYPELESS_G8X24_UINT = 22,
    DXGI_FORMAT_R10G10B10A2_TYPELESS = 23,
    DXGI_FORMAT_R10G10B10A2_UNORM = 24,
    DXGI_FORMAT_R10G10B10A2_UINT = 25,
    DXGI_FORMAT_R11G11B10_FLOAT = 26,
    DXGI_FORMAT_R8G8B8A8_TYPELESS = 27,
    DXGI_FORMAT_R8G8B8A8_UNORM = 28,
    DXGI_FORMAT_R8G8B8A8_UNORM_SRGB = 29,
    DXGI_FORMAT_R8G8B8A8_UINT = 30,
    DXGI_FORMAT_R8G8B8A8_SNORM = 31,
    DXGI_FORMAT_R8G8B8A8_SINT = 32,
    DXGI_FORMAT_R16G16_TYPELESS = 33,
    DXGI_FORMAT_R16G16_FLOAT = 34,
    DXGI_FORMAT_R16G16_UNORM = 35,
    DXGI_FORMAT_R16G16_UINT = 36,
    DXGI_FORMAT_R16G16_SNORM = 37,
    DXGI_FORMAT_R16G16_SINT = 38,
    DXGI_FORMAT_R32_TYPELESS = 39,
    DXGI_FORMAT_D32_FLOAT = 40,
    DXGI_FORMAT_R32_FLOAT = 41,
    DXGI_FORMAT_R32_UINT = 42,
    DXGI_FORMAT_R32_SINT = 43,
    DXGI_FORMAT_R24G8_TYPELESS = 44,
    DXGI_FORMAT_D24_UNORM_S8_UINT = 45,
    DXGI_FORMAT_R24_UNORM_X8_TYPELESS = 46,
    DXGI_FORMAT_X24_TYPELESS_G8_UINT = 47,
    DXGI_FORMAT_R8G8_TYPELESS = 48,
    DXGI_FORMAT_R8G8_UNORM = 49,
    DXGI_FORMAT_R8G8_UINT = 50,
    DXGI_FORMAT_R8G8_SNORM = 51,
    DXGI_FORMAT_R8G8_SINT = 52,
    DXGI_FORMAT_R16_TYPELESS = 53,
    DXGI_FORMAT_R16_FLOAT = 54,
    DXGI_FORMAT_D16_UNORM = 55,
    DXGI_FORMAT_R16_UNORM = 56,
    DXGI_FORMAT_R16_UINT = 57,
    DXGI_FORMAT_R16_SNORM = 58,
    DXGI_FORMAT_R16_SINT = 59,
    DXGI_FORMAT_R8_TYPELESS = 60,
    DXGI_FORMAT_R8_UNORM = 61,
    DXGI_FORMAT_R8_UINT = 62,
    DXGI_FORMAT_R8_SNORM = 63,
    DXGI_FORMAT_R8_SINT = 64,
    DXGI_FORMAT_A8_UNORM = 65,
    DXGI_FORMAT_R1_UNORM = 66,
    DXGI_FORMAT_R9G9B9E5_SHAREDEXP = 67,
    DXGI_FORMAT_R8G8_B8G8_UNORM = 68,
    DXGI_FORMAT_G8R8_G8B8_UNORM = 69,
    DXGI_FORMAT_BC1_TYPELESS = 70,
    DXGI_FORMAT_BC1_UNORM = 71,
    DXGI_FORMAT_BC1_UNORM_SRGB = 72,
    DXGI_FORMAT_BC2_TYPELESS = 73,
    DXGI_FORMAT_BC2_UNORM = 74,
    DXGI_FORMAT_BC2_UNORM_SRGB = 75,
    DXGI_FORMAT_BC3_TYPELESS = 76,
    DXGI_FORMAT_BC3_UNORM = 77,
    DXGI_FORMAT_BC3_UNORM_SRGB = 78,
    DXGI_FORMAT_BC4_TYPELESS = 79,
    DXGI_FORMAT_BC4_UNORM = 80,
    DXGI_FORMAT_BC4_SNORM = 81,
    DXGI_FORMAT_BC5_TYPELESS = 82,
    DXGI_FORMAT_BC5_UNORM = 83,
    DXGI_FORMAT_BC5_SNORM = 84,
    DXGI_FORMAT_B5G6R5_UNORM = 85,
    DXGI_FORMAT_B5G5R5A1_UNORM = 86,
    DXGI_FORMAT_B8G8R8A8_UNORM = 87,
    DXGI_FORMAT_B8G8R8X8_UNORM = 88,
    DXGI_FORMAT_R10G10B10_XR_BIAS_A2_UNORM = 89,
    DXGI_FORMAT_B8G8R8A8_TYPELESS = 90,
    DXGI_FORMAT_B8G8R8A8_UNORM_SRGB = 91,
    DXGI_FORMAT_B8G8R8X8_TYPELESS = 92,
    DXGI_FORMAT_B8G8R8X8_UNORM_SRGB = 93,
    DXGI_FORMAT_BC6H_TYPELESS = 94,
    DXGI_FORMAT_BC6H_UF16 = 95,
    DXGI_FORMAT_BC6H_SF16 = 96,
    DXGI_FORMAT_BC7_TYPELESS = 97,
    DXGI_FORMAT_BC7_UNORM = 98,
    DXGI_FORMAT_BC7_UNORM_SRGB = 99,
    DXGI_FORMAT_AYUV = 100,
    DXGI_FORMAT_Y410 = 101,
    DXGI_FORMAT_Y416 = 102,
    DXGI_FORMAT_NV12 = 103,
    DXGI_FORMAT_P010 = 104,
    DXGI_FORMAT_P016 = 105,
    DXGI_FORMAT_420_OPAQUE = 106,
    DXGI_FORMAT_YUY2 = 107,
    DXGI_FORMAT_Y210 = 108,
    DXGI_FORMAT_Y216 = 109,
    DXGI_FORMAT_NV11 = 110,
    DXGI_FORMAT_AI44 = 111,
    DXGI_FORMAT_IA44 = 112,
    DXGI_FORMAT_P8 = 113,
    DXGI_FORMAT_A8P8 = 114,
    DXGI_FORMAT_B4G4R4A4_UNORM = 115,
    DXGI_FORMAT_P208 = 130,
    DXGI_FORMAT_V208 = 131,
    DXGI_FORMAT_V408 = 132,
    DXGI_FORMAT_FORCE_UINT = 0xffffffff


format_map: Dict[decima.ImageStruct.ImageFormat, DXGI] = {
    decima.ImageStruct.ImageFormat.INVALID: DXGI.DXGI_FORMAT_UNKNOWN,
    # decima.ImageStruct.ImageFormat.RGBA_5551: ,
    # decima.ImageStruct.ImageFormat.RGBA_5551_REV: ,
    # decima.ImageStruct.ImageFormat.RGBA_4444: ,
    # decima.ImageStruct.ImageFormat.RGBA_4444_REV: ,
    # decima.ImageStruct.ImageFormat.RGB_888_32: ,
    # decima.ImageStruct.ImageFormat.RGB_888_32_REV: ,
    # decima.ImageStruct.ImageFormat.RGB_888: ,
    # decima.ImageStruct.ImageFormat.RGB_888_REV: ,
    # decima.ImageStruct.ImageFormat.RGB_565: ,
    # decima.ImageStruct.ImageFormat.RGB_565_REV: ,
    # decima.ImageStruct.ImageFormat.RGB_555: ,
    # decima.ImageStruct.ImageFormat.RGB_555_REV: ,
    decima.ImageStruct.ImageFormat.RGBA_8888: DXGI.DXGI_FORMAT_R8G8B8A8_TYPELESS,
    # decima.ImageStruct.ImageFormat.RGBA_8888_REV: ,
    # decima.ImageStruct.ImageFormat.RGBE_REV: ,
    decima.ImageStruct.ImageFormat.RGBA_FLOAT_32: DXGI.DXGI_FORMAT_R32G32B32A32_FLOAT,
    decima.ImageStruct.ImageFormat.RGB_FLOAT_32: DXGI.DXGI_FORMAT_R32G32B32_FLOAT,
    decima.ImageStruct.ImageFormat.RG_FLOAT_32: DXGI.DXGI_FORMAT_R32G32_FLOAT,
    decima.ImageStruct.ImageFormat.R_FLOAT_32: DXGI.DXGI_FORMAT_R32_FLOAT,
    decima.ImageStruct.ImageFormat.RGBA_FLOAT_16: DXGI.DXGI_FORMAT_R16G16B16A16_FLOAT,
    # decima.ImageStruct.ImageFormat.RGB_FLOAT_16: ,
    decima.ImageStruct.ImageFormat.RG_FLOAT_16: DXGI.DXGI_FORMAT_R16G16_FLOAT,
    decima.ImageStruct.ImageFormat.R_FLOAT_16: DXGI.DXGI_FORMAT_R16_FLOAT,
    # decima.ImageStruct.ImageFormat.RGBA_UNORM_32: ,
    # decima.ImageStruct.ImageFormat.RG_UNORM_32: ,
    # decima.ImageStruct.ImageFormat.R_UNORM_32: ,
    decima.ImageStruct.ImageFormat.RGBA_UNORM_16: DXGI.DXGI_FORMAT_R16G16B16A16_UNORM,
    decima.ImageStruct.ImageFormat.RG_UNORM_16: DXGI.DXGI_FORMAT_R16G16_UNORM,
    decima.ImageStruct.ImageFormat.R_UNORM_16: DXGI.DXGI_FORMAT_R16_UNORM,  # Old: INTENSITY_16
    decima.ImageStruct.ImageFormat.RGBA_UNORM_8: DXGI.DXGI_FORMAT_R8G8B8A8_UNORM,
    decima.ImageStruct.ImageFormat.RG_UNORM_8: DXGI.DXGI_FORMAT_R8G8_UNORM,
    decima.ImageStruct.ImageFormat.R_UNORM_8: DXGI.DXGI_FORMAT_R8_UNORM,  # Old: INTENSITY_8
    # decima.ImageStruct.ImageFormat.RGBA_NORM_32: ,
    # decima.ImageStruct.ImageFormat.RG_NORM_32: ,
    # decima.ImageStruct.ImageFormat.R_NORM_32: ,
    decima.ImageStruct.ImageFormat.RGBA_NORM_16: DXGI.DXGI_FORMAT_R16G16B16A16_SNORM,
    decima.ImageStruct.ImageFormat.RG_NORM_16: DXGI.DXGI_FORMAT_R16G16_SNORM,
    decima.ImageStruct.ImageFormat.R_NORM_16: DXGI.DXGI_FORMAT_R16_SNORM,
    decima.ImageStruct.ImageFormat.RGBA_NORM_8: DXGI.DXGI_FORMAT_R8G8B8A8_SNORM,
    decima.ImageStruct.ImageFormat.RG_NORM_8: DXGI.DXGI_FORMAT_R8G8_SNORM,
    decima.ImageStruct.ImageFormat.R_NORM_8: DXGI.DXGI_FORMAT_R8_SNORM,
    decima.ImageStruct.ImageFormat.RGBA_UINT_32: DXGI.DXGI_FORMAT_R32G32B32A32_UINT,
    decima.ImageStruct.ImageFormat.RG_UINT_32: DXGI.DXGI_FORMAT_R32G32_UINT,
    decima.ImageStruct.ImageFormat.R_UINT_32: DXGI.DXGI_FORMAT_R32_UINT,
    decima.ImageStruct.ImageFormat.RGBA_UINT_16: DXGI.DXGI_FORMAT_R16G16B16A16_UINT,
    decima.ImageStruct.ImageFormat.RG_UINT_16: DXGI.DXGI_FORMAT_R16G16_UINT,
    decima.ImageStruct.ImageFormat.R_UINT_16: DXGI.DXGI_FORMAT_R16_UINT,
    decima.ImageStruct.ImageFormat.RGBA_UINT_8: DXGI.DXGI_FORMAT_R8G8B8A8_UINT,
    decima.ImageStruct.ImageFormat.RG_UINT_8: DXGI.DXGI_FORMAT_R8G8_UINT,
    decima.ImageStruct.ImageFormat.R_UINT_8: DXGI.DXGI_FORMAT_R8_UINT,
    decima.ImageStruct.ImageFormat.RGBA_INT_32: DXGI.DXGI_FORMAT_R32G32B32A32_SINT,
    decima.ImageStruct.ImageFormat.RG_INT_32: DXGI.DXGI_FORMAT_R32G32_SINT,
    decima.ImageStruct.ImageFormat.R_INT_32: DXGI.DXGI_FORMAT_R32_SINT,
    decima.ImageStruct.ImageFormat.RGBA_INT_16: DXGI.DXGI_FORMAT_R16G16B16A16_SINT,
    decima.ImageStruct.ImageFormat.RG_INT_16: DXGI.DXGI_FORMAT_R16G16_SINT,
    decima.ImageStruct.ImageFormat.R_INT_16: DXGI.DXGI_FORMAT_R16_SINT,
    decima.ImageStruct.ImageFormat.RGBA_INT_8: DXGI.DXGI_FORMAT_R8G8B8A8_SINT,
    decima.ImageStruct.ImageFormat.RG_INT_8: DXGI.DXGI_FORMAT_R8G8_SINT,
    decima.ImageStruct.ImageFormat.R_INT_8: DXGI.DXGI_FORMAT_R8_SINT,
    decima.ImageStruct.ImageFormat.RGB_FLOAT_11_11_10: DXGI.DXGI_FORMAT_R11G11B10_FLOAT,
    decima.ImageStruct.ImageFormat.RGBA_UNORM_10_10_10_2: DXGI.DXGI_FORMAT_R10G10B10A2_UNORM,
    # decima.ImageStruct.ImageFormat.RGB_UNORM_11_11_10: ,
    decima.ImageStruct.ImageFormat.DEPTH_FLOAT_32_STENCIL_8: DXGI.DXGI_FORMAT_D32_FLOAT_S8X24_UINT,  # TODO: Confirm
    decima.ImageStruct.ImageFormat.DEPTH_FLOAT_32_STENCIL_0: DXGI.DXGI_FORMAT_D32_FLOAT,
    decima.ImageStruct.ImageFormat.DEPTH_24_STENCIL_8: DXGI.DXGI_FORMAT_D24_UNORM_S8_UINT,  # TODO: Confirm
    decima.ImageStruct.ImageFormat.DEPTH_16_STENCIL_0: DXGI.DXGI_FORMAT_D16_UNORM,  # TODO: Confirm
    decima.ImageStruct.ImageFormat.BC1: DXGI.DXGI_FORMAT_BC1_UNORM,  # Old: S3TC1
    decima.ImageStruct.ImageFormat.BC2: DXGI.DXGI_FORMAT_BC2_UNORM,  # Old: S3TC3
    decima.ImageStruct.ImageFormat.BC3: DXGI.DXGI_FORMAT_BC3_UNORM,  # Old: S3TC5
    decima.ImageStruct.ImageFormat.BC4U: DXGI.DXGI_FORMAT_BC4_UNORM,
    decima.ImageStruct.ImageFormat.BC4S: DXGI.DXGI_FORMAT_BC4_SNORM,
    decima.ImageStruct.ImageFormat.BC5U: DXGI.DXGI_FORMAT_BC5_UNORM,
    decima.ImageStruct.ImageFormat.BC5S: DXGI.DXGI_FORMAT_BC5_SNORM,
    decima.ImageStruct.ImageFormat.BC6U: DXGI.DXGI_FORMAT_BC6H_UF16,
    decima.ImageStruct.ImageFormat.BC6S: DXGI.DXGI_FORMAT_BC6H_SF16,
    decima.ImageStruct.ImageFormat.BC7: DXGI.DXGI_FORMAT_BC7_UNORM
}


def build_dds_header(texture: decima.ImageStruct) -> bytes:
    header_data = bytes()

    flags = b'\x07\x10\x00\x00'  # TODO
    header_data += flags

    header_data += struct.pack('<I', texture.height)  # height
    header_data += struct.pack('<I', texture.width)  # width
    header_data += struct.pack('<I', texture.size_without_stream + texture.size_of_stream)  # pitchOrLinearSize
    header_data += struct.pack('<I', 0)  # TODO: Depth
    header_data += struct.pack('<I', texture.mipmaps_in_stream + 1 if hasattr(texture, "mipmaps_in_stream") else 1)
    header_data += (b'\x00' * 4) * 11  # reserved

    # TODO: PixelFormat
    # Stubbed implementation, this just states that there will be a DX10 header
    pixel_format = bytes()

    pixel_format += struct.pack('<I', 4)  # flags - specifically, DDPF_FOURCC
    pixel_format += b'DX10'  # FourCC
    pixel_format += struct.pack('<I', 0)  # RGBBitCount
    pixel_format += struct.pack('<I', 0)  # Red bit mask
    pixel_format += struct.pack('<I', 0)  # Green bit mask
    pixel_format += struct.pack('<I', 0)  # Blue bit mask
    pixel_format += struct.pack('<I', 0)  # Alpha bit mask

    assert len(pixel_format) == 32 - 4
    header_data += struct.pack('<I', len(pixel_format) + 4)
    header_data += pixel_format

    # TODO: caps
    header_data += struct.pack('<I', 0)  # caps 1
    header_data += struct.pack('<I', 0)  # caps 2
    header_data += struct.pack('<I', 0)  # caps 3
    header_data += struct.pack('<I', 0)  # caps 4
    header_data += struct.pack('<I', 0)  # reserved 2

    assert len(header_data) == 124 - 4
    header_data = b'DDS ' + struct.pack('<I', len(header_data) + 4) + header_data

    # DX10 Header
    dx10_header = b''
    assert texture.image_format in format_map, f"Unmapped image format: {texture.image_format.name}"
    dx10_header += struct.pack('<I', format_map[texture.image_format].value)  # format
    dx10_header += struct.pack('<I', 3)  # TODO: dimension, currently forced to 2D
    dx10_header += struct.pack('<I', 0)  # miscFlags
    dx10_header += struct.pack('<I', 1)  # arraySize
    dx10_header += struct.pack('<I', 0)  # miscFlags2

    header_data += dx10_header

    return header_data


def dump_texture(data: decima.ImageStruct, out_path: str):
    print(f'  {os.path.split(out_path)[1]} {data.image_format.name}')
    stream_data = bytes()
    if hasattr(data, "size_of_stream") and data.size_of_stream > 0:
        cache_path = data.cache_string
        assert cache_path.startswith("cache:")
        game_root = decima.game_root_ps4 if decima.is_ps4 else decima.game_root_pc
        stream_path = os.path.join(game_root, cache_path[6:])
        assert os.path.isfile(stream_path), f"Missing stream file {stream_path}"
        stream_file = open(stream_path, 'rb')
        stream_file.seek(data.stream_start)
        stream_data = stream_file.read(data.size_of_stream)
    out_file = open(out_path, 'wb')
    out_file.write(build_dds_header(data))
    out_file.write(stream_data)
    out_file.write(data.image_contents)


def print_channel_details(
        channel_details: List[decima.TextureSet.TextureDetails.ChannelDetails],
        sources: List[decima.TextureSet.SourceDetails]):
    channels = 'RGBA'
    maps = dict()
    for i, channel in enumerate(channel_details):
        if channel.unk == 8 or channel.setType.name not in maps:
            maps[channel.setType.name] = channels[i]
        else:
            maps[channel.setType.name] += channels[i]
    for i in maps:
        source = [s for s in sources if s.set_type.name == i]
        source_name = ""
        if len(source) == 1 and len(source[0].source_filename) > 0:
            source_name = f' ({source[0].source_filename[5:]})'
        print(f'    {maps[i]} = {i}{source_name}')


def dump_core(filename):
    print(filename)
    script_objects: Dict[bytes, decima.Resource] = {}
    decima.read_objects(filename, script_objects)
    dumped_textures: Set[bytes] = set()
    dumped_paths: Set[str] = set()

    # Look for any texture sets and dump their contents
    for obj in script_objects.values():
        if isinstance(obj, decima.TextureSet):
            print(f'{obj.type}: {obj.name}')
            for tex in obj.textures:
                tex_res = tex.texture.follow(script_objects)
                out_path = os.path.join(os.path.split(filename)[0], tex_res.name + '.dds')
                assert out_path not in dumped_paths, f"Name conflict: {tex_res.name}.dds already dumped"
                dump_texture(tex_res.image_data, out_path)
                dumped_textures.add(tex.texture.hash)
                if not tex_res.name.startswith("SingleColorTexture_"):
                    dumped_paths.add(out_path)
                print_channel_details(tex.channel_details, obj.sources)

    # Second pass through, looking for textures _not_ in sets now
    for uuid in script_objects:
        obj = script_objects[uuid]
        if isinstance(obj, decima.Texture) and uuid not in dumped_textures:
            print(f'{obj.type}: {obj.name}')
            out_path = os.path.join(os.path.split(filename)[0], obj.name + '.dds')
            assert out_path not in dumped_paths
            dump_texture(obj.image_data, out_path)
            if not (obj.name.startswith("SingleColorTexture_") or obj.name.startswith("RampTexture")):
                dumped_paths.add(out_path)
        if isinstance(obj, decima.UITexture):
            print(f'{obj.type}: {obj.name_1}')
            out_path = os.path.join(os.path.split(filename)[0], obj.name_1 + '.dds')
            assert out_path not in dumped_paths, f"Name conflict: {obj.name_1}.dds already dumped"
            if obj.image_data is not None:
                if obj.image_data_2 is not None:
                    dump_texture(obj.image_data_2, out_path)
                else:
                    dump_texture(obj.image_data, out_path)
            if not obj.name_1.startswith("SingleColorTexture_"):
                dumped_paths.add(out_path)


def dump_recursive(directory: str):
    for root, directories, filenames in os.walk(directory):
        for f in filenames:
            if os.path.splitext(f)[1] == ".core":
                dump_core(os.path.join(root, f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str,
                        help="Path to a .core file containing textures, or a directory to recursively dump from.")
    args = parser.parse_args()
    if os.path.isfile(args.path) and os.path.splitext(args.path)[1] == ".core":
        dump_core(args.path)
    elif os.path.isdir(args.path):
        dump_recursive(args.path)
    else:
        raise Exception(f'"{args.path}" is not a .core file or a directory.')


if __name__ == '__main__':
    main()
