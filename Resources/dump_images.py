import glob
import json
import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup


DEFAULT_IPAD_SCALE = 1.25


def get_bool_option(short_option, long_option):
    option = False
    if short_option in sys.argv:
        option = True
        sys.argv.remove(short_option)
    if long_option in sys.argv:
        option = True
        sys.argv.remove(long_option)
    return option


def get_option(short_option, long_option):
    option = None

    short_option_index = None
    for i, arg in enumerate(sys.argv):
        if arg == short_option:
            short_option_index = i
            break
    if short_option_index is not None:
        option = sys.argv[short_option_index + 1]
        del sys.argv[short_option_index: short_option_index + 2]

    long_option_index = None
    for i, arg in enumerate(sys.argv):
        if arg == long_option:
            long_option_index = i
            break
    if long_option_index is not None:
        option = sys.argv[long_option_index + 1]
        del sys.argv[long_option_index: long_option_index + 2]

    return option


dryrun = get_bool_option("-n", "--dry-run")
verbose = get_bool_option("-v", "--verbose")
overwrite = get_bool_option("-f", "--force")
optimize = get_bool_option("-o", "--optimize")
export_drawing = get_bool_option("-D", "--export-area-drawing")
use_layer_name = get_bool_option("-l", "--use-layer-name")
trim_transparent = get_bool_option("-t", "--trim-transparent")
merge_layers = get_bool_option("-m", "--merge-layers")
omit_ipad_images = get_bool_option("-u", "--omit-ipad-images")
omit_1x_iphone_image = get_bool_option("-2", "--omit-1x-iphone-image")
border = get_option("-b", "--border") # Percent of max(width, height) to use as border
image_scale = get_option("-s", "--scale")
colorize = get_option("-c", "--colorize")
ipad_scale = get_option("-p", "--ipad-scale")

if not ipad_scale:
    ipad_scale = DEFAULT_IPAD_SCALE
ipad_scale = float(ipad_scale)

if border:
    border = float(border)

if export_drawing:
    export_flag = "-D"
else:
    export_flag = "-C"

if dryrun and not verbose:
    inkscape = "inkscape"
    imageoptim = "ImageOptim"
    convert = "convert"
else:
    inkscape = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
    imageoptim = "/Applications/ImageOptim.app/Contents/MacOS/ImageOptim"
    convert = "/usr/local/bin/convert"


base_outdir = os.path.abspath("../static/images")
arg_iphone_size_re = re.compile(r"^(\d+)[xX](\d+)$")
arg_ipad_size_re = re.compile(r"^ipad(\d+)[xX](\d+)$")
iphone_size_re = re.compile(r"_(\d+)[xX](\d+)")
ipad_size_re = re.compile(r"_ipad(\d+)[xX](\d+)")

args = sys.argv[1:]
files = []
arg_iphone_w, arg_iphone_h = 0, 0
arg_ipad_w, arg_ipad_h = 0, 0

for arg in args:
    m = arg_ipad_size_re.match(arg)
    if m:
        arg_ipad_w, arg_ipad_h = int(m.group(1)), int(m.group(2))
    else:
        m = arg_iphone_size_re.match(arg)
        if m:
            arg_iphone_w, arg_iphone_h = int(m.group(1)), int(m.group(2))
        else:
            files.append(arg)

if image_scale:
    image_scale = float(image_scale)

if not files:
    print("At least one image file must be specified")
    sys.exit(1)


def log(s, force=False):
    if verbose or force:
        print(s)


def analyze_svg(svg):
    data = {}
    xml = open(svg, "r").read()
    soup = BeautifulSoup(xml, features="xml")
    data["width"] = soup.svg["width"]
    data["height"] = soup.svg["height"]
    data["layers"] = {}
    for layer in soup.svg.find_all("g", attrs={"inkscape:groupmode": "layer"}):
        if "display:none" not in layer.get("style", ""):
            data["layers"][layer["id"]] = {
                "name": layer["inkscape:label"],
                "id" : layer["id"]
            }
    return data


def execute(cmd):
    log(" ".join(cmd), force=dryrun)
    if dryrun:
        return ""
    else:
        return subprocess.check_output(cmd).decode("utf-8")


def dump_json(obj, path):
    # log(path)
    log(json.dumps(obj, indent=2))
    # if not dryrun:
    #     json.dump(obj, open(path, "w"), indent=2)


files_to_optimize = []

for svg in files:
    svg = os.path.abspath(svg)
    rel_path = os.path.dirname(os.path.relpath(svg))
    source_time = os.path.getmtime(svg)
    svg_data = analyze_svg(svg)

    svg_name = svg

    ipad_w, ipad_h = 0, 0
    m = ipad_size_re.search(svg_name)
    if m:
        ipad_w, ipad_h = int(m.group(1)), int(m.group(2))
        svg_name = svg_name[:m.start()] + svg_name[m.end():]

    iphone_w, iphone_h = 0, 0
    m = iphone_size_re.search(svg_name)
    if m:
        iphone_w, iphone_h = int(m.group(1)), int(m.group(2))
        svg_name = svg_name[:m.start()] + svg_name[m.end():]

    if arg_iphone_w and arg_iphone_h:
        iphone_w, iphone_h = arg_iphone_w, arg_iphone_h
        log("Using iphone size from command line: {}x{}".format(iphone_w, iphone_h))
    elif iphone_w and iphone_h:
        log("Using iphone size from filename: {}x{}".format(iphone_w, iphone_h))
    else:
        iphone_w, iphone_h = int(svg_data["width"]), int(svg_data["height"])
        log("Using iphone size from svg document: {}x{}".format(iphone_w, iphone_h))

    if omit_ipad_images:
        log("Using large iphone images for ipad idiom")
    else:
        if arg_ipad_w and arg_ipad_h:
            ipad_w, ipad_h = arg_ipad_w, arg_ipad_h
            log("Using ipad size from command line: {}x{}".format(ipad_w, ipad_h))
        elif ipad_w and ipad_h:
            log("Using ipad size from filename: {}x{}".format(ipad_w, ipad_h))
        else:
            ipad_w, ipad_h = int(round(ipad_scale * iphone_w)), int(round(ipad_scale * iphone_h))
            log("Upsizing iphone size: {}x{} for ipad: {}x{}".format(iphone_w, iphone_h, ipad_w, ipad_h))

    if image_scale:
        iphone_w, iphone_h = int(round(iphone_w * image_scale)), int(round(iphone_h * image_scale))
        log("Scaling iphone size by {} to {}x{}".format(image_scale, iphone_w, iphone_h))
        if not omit_ipad_images:
            ipad_w, ipad_h = int(round(ipad_w * image_scale)), int(round(ipad_h * image_scale))
            log("Scaling ipad size by {} to {}x{}".format(image_scale, ipad_w, ipad_h))

    basename = os.path.basename(svg_name[:-4])

    image_sizes = [(1.0, "", "iphone"), (2.0, "@2x", "iphone")]
    # suffix_1x = "@2x" if omit_1x_iphone_image else ""
    # image_sizes = [(1.0, suffix_1x, "iphone"), (2.0, "@2x", "iphone"), (3.0, "@3x", "iphone")]
    # if omit_ipad_images:
    #     image_sizes.extend([(1.0, "@2x", "ipad"), (2.0, "@3x", "ipad")])
    # else:
    #     image_sizes.extend([(1.0, "~ipad", "ipad"), (2.0, "@2x~ipad", "ipad")])

    def export_svg(outdir, layer_id=None, layer_name=None):
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        contents = {
            "images" : [],
            "info" : {
                "version" : 1,
                "author" : "xcode"
            }
        }

        for (scale, scale_suffix, idiom) in image_sizes:
            if layer_name:
                filename = "{}_{}{}.png".format(basename, layer_name, scale_suffix)
            else:
                filename = "{}{}.png".format(basename, scale_suffix)
            output = "{}/{}".format(outdir, filename)

            contents["images"].append({
                "idiom" : idiom,
                "scale" : "{}x".format(int(scale)),
                "filename" : filename
            })

            if idiom == "ipad" and omit_ipad_images:
                continue

            if overwrite or not os.path.exists(output) or source_time > os.path.getmtime(output):
                if idiom == "ipad":
                    w, h = ipad_w, ipad_h
                else:
                    w, h = iphone_w, iphone_h
                cmd = [inkscape, "--export-background-opacity=0"]
                if layer_id:
                    cmd.extend(["-i", layer_id, "-j"])
                cmd.extend([export_flag, "-o", output, "-w", str(int(w * scale)), "-h", str(int(h * scale)), svg])
                execute(cmd)
                if trim_transparent:
                    cmd = [convert, output, "-bordercolor", "none", "-border", "3x3", "-trim", "+repage", output]
                    execute(cmd)
                if border:
                    b = round(max(w, h) * (border / 100.0)) * scale
                    cmd = [convert, output, "-bordercolor", "none", "-border", "{}x{}".format(b, b), output]
                    execute(cmd)
                if colorize:
                    cmd = [convert, output, "-fill", colorize, "-colorize", "100%", output]
                    execute(cmd)
                if optimize:
                    files_to_optimize.append(output)

        dump_json(contents, "{}/Contents.json".format(outdir))

    multi_layer = len(svg_data["layers"]) > 1
    if not merge_layers and (use_layer_name or multi_layer):
        for layer_id, layer in svg_data["layers"].items():
            # outdir = "{}/{}.xcassets/{}_{}.imageset".format(base_outdir, rel_path, basename, layer["name"])
            outdir = base_outdir
            export_svg(outdir, layer_id=layer_id, layer_name=layer["name"])
    else:
        # outdir = "{}/{}.xcassets/{}.imageset".format(base_outdir, rel_path, basename)
        outdir = base_outdir
        export_svg(outdir)


if files_to_optimize:
    cmd = [imageoptim] + files_to_optimize
    execute(cmd)
