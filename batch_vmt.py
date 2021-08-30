#!/usr/bin/env python3
# batch_vmt (c) by Bikkie / snake-biscuits [b!scuit#3659]
#
# batch_vmt is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
"""generate .vmt files from a folder of .vtf files"""
from __future__ import annotations
import argparse
import fnmatch
import os
import re
from typing import Dict, List, Tuple

from colour import Color
# from gooey import Gooey

# import VTFLibWrapper


__version__ = "1.0.0"


def from_template(vtf_filename: str, template: str, **substitutions: Dict[str, str]):
    """Generate .vmts from `template` for every .vtf in `folder`"""
    # example usage:
    # from_template("LightmappedGeneric{$basetexture <filename>}", "materials/folder")
    # from_template(open("template.vmt").read(), "materials/folder", surfaceprop="metal")
    for keyword, replacement in substitutions.items():
        template = template.replace(f"<{keyword}>", replacement)
        # e.g. replacements = {"texture2": "<filename>a"}
        # '$basetexture2 <texture2>' --> '"$blendmodulatetexture" "<filename>_bm"'
        # then at the file level: '<filename>_bm' -> 'texture_bm' for "texture.vmt"
    # NOTE: never put filename in replacements unless you want to replace all textures with one texture!
    filename = os.path.splitext(vtf_filename)[0]  # remove .vtf extension
    with open(f"{filename}.vmt", "w") as vmt_file:
        vmt_file.write(template.replace("<filename>", filename))


# TODO: maybe separate file filtering from .vmt writing?
def from_metadata(vtf_filename: str, shader: str = "LightmappedGeneric", **flags: Dict[str, Tuple[str, str]]):
    """generate an appropriate .vmt from .vmt flags"""
    raise NotImplementedError()
    # * EXPECTED FLAGS *
    # has_alpha: bool   // vtf is transparent e.g. {"has_alpha": "$translucent": 1}
    # colour: Color     // fuzzy colour detection
    # hue_range: float  // [0-1]; how close the texture's hue should be to colour

    filename = os.path.splitext(vtf_filename)[0]

    vtf = ...  # TODO: load f"{filename}.vtf" with VTFLibWrapper
    # check flags
    if "color" in flags:
        flags["colour"] = flags.pop("color")
    if "transparent" in flags:
        flags["has_alpha"] = flags.pop("transparent")
    checks: Dict[str, bool]
    checks = {"colour": fuzzy_colour_match(vtf.reflectivity, flags["colour"], flags.get("hue_range", 0)),
              "has_alpha": has_alpha(vtf),
              None: None}
    # ^ {"flag": True or False}
    metadata = {f: checks.get(f, None) for f in flags}

    # compose the .vmt text
    lines = [shader, "{"]
    for flag in flags:
        parameter, value = flags[flag]
        if metadata[flag] is True:
            lines.append('\t"{paramater}" "{value}"')
    lines.append("}")
    # write to file
    with open(f"{filename}.vmt", "w") as vmt_file:
        vmt_file.write("\n".join(lines))


# check functions for from_metadata
def fuzzy_colour_match(a: Color, b: Color, hue_range: float) -> bool:
    return abs(a.hsl[0] - b.hsl[0]) <= hue_range


def has_alpha(vtf) -> bool:
    raise NotImplementedError()
    return vtf.image_format in (...)


def parse_folder(method: str, folders: List[str], template=None, ignore=[], recursive=False, verbose=False, **kwargs):
    # pre-processing
    ignore_patterns = [re.compile(p) for p in ignore]
    if method == "template":
        # kwargs["substutions"]: Dict[str, str] = {"keyword": "replacement"}
        template = open(template).read()
        # NOTE: the "template" kwarg must be supplied! [process_folder(..., template="base.vmt")]
        # template substitutions
        for keyword, replacement in kwargs.pop("substitutions", dict()).items():
            template = template.replace(f"<{keyword}>", replacement)
    elif method == "metadata":
        # kwargs = {"flags": Dict[str, Tuple[str, str]], shader: str}
        # flags = {"flag": ("$parameter", "value")}
        from_metadata(method)
    else:
        raise RuntimeError("Invalid method: '{method}', only 'template' & 'metadata' are accepted")

    # parse all folders
    for folder in folders:
        folder_contents = [os.path.join(f) for f in os.listdir(folder)]
        if recursive:
            folders.extend([d for d in folder_contents if os.path.isdir(d)])
        for vtf_filename in fnmatch.filter(folder_contents, "*.vtf"):
            filename = os.path.join(folder, os.path.splitext(vtf_filename)[0])
            if any([pattern.match(filename) for pattern in ignore_patterns]):
                if verbose:
                    print("Skipping {filename}.vmt")
                continue
            # process file
            if verbose:
                print(f"Writing {filename}.vmt... ", end="")
            if method == "template":
                from_template(filename, template)
            elif method == "metadata":
                # TODO: do a keyword substitution pass on flags.values
                from_metadata(filename, **kwargs)
            if verbose:
                print("Done!")


# @Gooey
def main(with_args: List[str] = None):
    notes = ["You can drag any folder over %(prog)s and just use the defaults",
             "--template (default: base.vmt next to %(prog)s) must have a <filename> keyword!",
             "--replace KEYWORD:REPLACEMENT will replace any keyword",
             "However, if no replacement is given, lines with <keyword> will remain and break .vmt",
             " \nYou should find a displacement_base.vmt included with %(prog)s",
             "--ignore .*_a .*_bump .*_bm .*_editor should be used when generating displacements"]

    parser = argparse.ArgumentParser(description=__doc__, epilog="\n".join(notes),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folders", nargs="*",
                        help="folder to generate .vmts for (one for each .vtf)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-t", "--template", default="base.vmt",
                      help="generate vmts from the supplied template\ndefault: base.vmt")
    mode.add_argument("-m", "--metadata", action="store_true",
                      help="generate each .vmt based on flags set in the .vtf\nNOT IMPLEMENTED YET")
    parser.add_argument("-f", "--flags",
                        help="colon separated metadata flags\n(e.g. has_alpha:$translucent:1)\nNOT IMPLEMENTED YET")
    # TODO: set vmt shader (default: LightmappedGeneric)
    # TODO: list all available flags
    parser.add_argument("-s", "--substitute", action="append", metavar="keyword:replacement", default=[],
                        help="substitute <keyword> in template with replacement\n(e.g. `bumpmap:<filename>_bump`)")
    parser.add_argument("-r", "--recurse", action="store_true",
                        help="generate .vmts for all folders within folder")
    parser.add_argument("-i", "--ignore", action="append", metavar="patterns", nargs="*", default=[],
                        help="skip <filename> if it matches any of the given patterns")
    # TODO: --generate (metadata based .vmt & adding / removing relevant key-value pairs [no template])
    # TODO: --surfaceprop choice to add a surfaceprop
    # TODO: match replacements to filename from a .csv
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print each filename as it is processed")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s v{__version__}")

    if with_args is not None:
        args = parser.parse_args(with_args)
    else:
        args = parser.parse_args()

    # if not args.metadata:  # template mode
    replacements = {k.strip("<>"): v for a in args.substitute for k, v in a.split(":")}
    # replacements are colon separated; < & > around the keyword are optional
    # setting filename will give all make all .vmts generated identical! even the basetexture!
    parse_folder("template", args.folders, template=args.template, substitutions=replacements,
                 ignore=args.ignore, verbose=args.verbose)
    # else:  # metadata mode
    # flags = {f: (p, v) for m in args.metadata for f, p, v in m.split(":")}
    # process_folder("metadata", args.folders, flags=flags,
    #                ignore=args.ignore, verbose=args.verbose)


if __name__ == "__main__":
    main()
