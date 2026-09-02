from PIL import Image, ImageOps, ImageFilter
import subprocess, os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def ocr(path, psm=7):
    outbase = path + ".out"
    subprocess.run([TESS, path, outbase, "--psm", str(psm),
                    "-c", "tessedit_char_whitelist=" + WHITELIST],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with open(outbase + ".txt", encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ""

def analyze(src):
    img = Image.open(src)
    print('original size:', img.size, 'mode:', img.mode)
    w, h = img.size
    big = img.convert('RGB').resize((w * 4, h * 4), Image.LANCZOS)
    g = big.convert('L')

    variants = {
        'big_gray': g,
        'autocontrast': ImageOps.autocontrast(g),
        'thr140': g.point(lambda x: 255 if x > 140 else 0),
        'thr160': g.point(lambda x: 255 if x > 160 else 0),
        'thr180': g.point(lambda x: 255 if x > 180 else 0),
        'sharpen': g.filter(ImageFilter.SHARPEN),
    }
    results = []
    for name, im in variants.items():
        p = os.path.join(BASE_DIR, f'cap_{name}.png')
        im.save(p)
        r7 = ocr(p, 7)
        r8 = ocr(p, 8)
        results.append((name, r7, r8))
        print(f'{name:14s} psm7=[{r7}]  psm8=[{r8}]')
    return results

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, 'captcha.jpg')
    analyze(src)
