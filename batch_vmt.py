# batch_vmt (c) by Bikkie / snake-biscuits [b!scuit#3659]
#
# batch_vmt is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
"""generate .vmt files from a folder of .vtf files"""
from __future__ import annotations
import fnmatch
import os
from typing import Dict, List

from colour import Color
from gooey import Gooey, GooeyParser

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
        # '$basetexture2 <blend_texture>' --> '"$basetexture2" "<filename>_a"'
        # then at the file level: '<filename>_a' -> 'texture_a' for "texture.vmt"
    # NOTE: never put filename in replacements unless you want to replace all textures with one texture!
    filename = os.path.splitext(vtf_filename)[0]  # remove .vtf extension
    with open(f"{filename}.vmt", "w") as vmt_file:
        vmt_file.write(template.replace("<filename>", filename))


# TODO: maybe separate file filtering from .vmt writing?
def from_metadata(vtf_filename: str, shader: str = "LightmappedGeneric",
                  colour=Color("White"), hue_range: float = 0,
                  defaults={"colour": ("%keywords", "white")}):
    """generate an appropriate .vmt from .vmt flags"""
    raise NotImplementedError()
    # * EXPECTED FLAGS *
    # has_alpha: bool   // vtf is transparent e.g. {"has_alpha": "$translucent": 1}
    # colour: Color     // fuzzy colour detection
    # hue_range: float  // [0-1]; how close the texture's hue should be to colour

    filename = os.path.splitext(vtf_filename)[0]

    vtf = ...  # TODO: load f"{filename}.vtf" with VTFLibWrapper
    # check flags
    check: Dict[str, bool]
    check = {"colour": fuzzy_colour_match(vtf.reflectivity, colour, hue_range),
             "has_alpha": has_alpha(vtf)}
    # ^ {"flag": True or False}

    # compose the .vmt text
    lines = [shader, "{"]
    for condition in check:
        parameter, value = defaults[condition]
        if check[condition] is True:
            value = value.replace("<filename>", filename)
            lines.append('\t"{paramater}" "{value}"')
    lines.append("}")
    # write to file
    with open(f"{filename}.vmt", "w") as vmt_file:
        vmt_file.write("\n".join(lines))


# check functions for from_metadata
def fuzzy_colour_match(a: Color, b: Color, hue_range: float) -> bool:
    # TODO: accept a hue_range or rgb_range 3-ple
    return abs(a.hsl[0] - b.hsl[0]) <= hue_range


def has_alpha(vtf) -> bool:
    raise NotImplementedError()
    return "A" in vtf.image_format.name  # NOTE: untested


# TODO: split for both modes? or is it still easier to process folder recursion here?
def parse_folder(method: str, folders: List[str], template=None, **kwargs):
    # pre-processing
    if method == "template":
        # kwargs["substutions"]: Dict[str, str] = {"keyword": "replacement"}
        template = open(template).read()
        # NOTE: the "template" kwarg must be supplied! [process_folder(..., template="base.vmt")]
        # template substitutions
        for keyword, replacement in kwargs.pop("substitutions", dict()).items():
            template = template.replace(f"<{keyword}>", replacement)
    elif method == "metadata":
        # TODO: figure out what can be pre-processes for metadata batches
        from_metadata(method)  # NotImplemented!
    else:
        raise RuntimeError("Invalid method: '{method}', only 'template' & 'metadata' are accepted")

    # parse all folders
    for folder in folders:
        folder_contents = [os.path.join(f) for f in os.listdir(folder)]
        folders.extend([d for d in folder_contents if os.path.isdir(d)])
        # NOTE: this isn't recursing folders like I thought it would...
        for vtf_filename in fnmatch.filter(folder_contents, "*.vtf"):
            filename = os.path.join(folder, os.path.splitext(vtf_filename)[0])
            # process file
            print(f"Writing {filename}.vmt... ", end="")
            if method == "template":
                from_template(filename, template)
            elif method == "metadata":
                # TODO: do a keyword substitution pass on flags.values
                from_metadata(filename, **kwargs)
            print("Done!")


@Gooey
def main():
    # NOTES:
    # --template (default: base.vmt next to batch_vmt.py must have a <filename> keyword!
    # --replace KEYWORD:REPLACEMENT will replace any keyword
    # However, if no replacement is given, lines with <keyword> will remain and break .vmt
    # Also, You should find a displacement_base.vmt included with batch_vmt.py
    # --ignore .*_a .*_bump .*_bm .*_editor should be used when generating displacements

    parser = GooeyParser(description=__doc__)
    parser.add_argument("filenames", nargs="*", metavar="FILE", widget="MultiFileChooser", default="tests/materials",
                        help="filename(s) / folder(s) to generate .vmts for\nFolders must be typed in manually")
    parser.add_argument("-t", "--template", default="base.vmt", widget="FileChooser",
                        help="generate vmts from the supplied template\ndefault: base.vmt")
    # subparsers = parser.add_subparsers(title="mode", description="mode to run in")
    # template_mode = subparsers.add_parser("template")
    parser.add_argument("-s", "--substitute", nargs="*", default="tags:generated",
                        help="substitute <keyword> in template with replacement\n(e.g. `bumpmap:<filename>_bump`)")
    # ...
    # generate_mode = subparsers.add_parser("generate")
    # TODO: --surfaceprop choice to add a surfaceprop
    # TODO: --hsv_range H:S:V
    # TODO: --rgb_range R:G:B
    # TODO: --colour "White":"$parameter":"<keyword>"
    # ...
    args = parser.parse_args()

    folders = list(filter(os.path.isdir, args.filenames))
    filenames = set(args.filenames).difference(set(folders))
    # TODO: handle any wildcards in filenames

    # TODO: handle both modes here
    # if args.generate:
    # process_folder("metadata", folders, ...)
    # for filename in filenames:
    #     from_metadata(filename, ...)
    # else:  # template mode
    replacements = dict()
    for kr in args.substitute:
        k, r = kr.split(":")
        replacements[k] = r
    # replacements are colon separated; < & > around the keyword are optional
    # setting <filename> will give all make all .vmts generated identical! even the basetexture!
    parse_folder("template", folders, template=args.template, substitutions=replacements)
    for filename in filenames:
        from_template(filename, args.template, substitutions=replacements)


if __name__ == "__main__":
    main()  # run the Gooey UI
