import os
import sys
from multiprocessing import Pool, cpu_count
from PIL import Image


# Get all files to be processed
def scan(original_root: str):
    files_to_compress = []
    for root, dirs, files in os.walk(original_root):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                files_to_compress.append(os.path.join(root, file))
    return files_to_compress


# Compress image at path
def compress(path: str):
    if path.endswith(".jpg") or path.endswith(".jpeg"):
        try:
            img = Image.open(path)
            img.save(path, "JPEG", optimize=True, quality=90)
        except Exception as e:
            print("Could not process file %s" % path)
    elif path.endswith(".png"):
        try:
            img = Image.open(path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(path.replace(".png", ".jpg"), "JPEG", optimize=True, quality=90)
            os.remove(path)
        except Exception as e:
            print("Could not process file %s" % path)
    print("Processed %s" % path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify folder to compress!")
        sys.exit(1)

    original_root = os.path.join(sys.argv[1])

    if not os.path.isdir(original_root):
        print("Folder not found!")
        sys.exit(1)

    files_to_compress = scan(original_root)

    with Pool(processes=cpu_count()) as pool:
        pool.map(compress, files_to_compress)

    input("Done. Press Enter to exit.")