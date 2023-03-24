import os
import sys
from multiprocessing import Pool, cpu_count
from PIL import Image


def scan(original_root: str):
    files_to_compress = []
    for root, dirs, files in os.walk(original_root):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                files_to_compress.append(os.path.join(root, file))
    return files_to_compress


def compress(path: str):
    if path.endswith(".jpg") or path.endswith(".jpeg"):
        img = Image.open(path)
        img.save(path, "JPEG", optimize=True, quality=90)
    elif path.endswith(".png"):
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(path.replace(".png", ".jpg"), "JPEG", optimize=True, quality=90)
        os.remove(path)
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
        for f in files_to_compress:
            pool.apply(compress, args=(f,))

    input("Done. Press Enter to exit.")
