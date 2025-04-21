import hashlib, numpy as np, random
from numpy.random import default_rng
from PIL import Image

class TripathiBuffer:
    @staticmethod
    def get_seed_from_string(s: str) -> int:
        h = hashlib.sha256(s.encode()).hexdigest()
        return int(h, 16) % 2**32

    @staticmethod
    def generate_noise_from_seed(seed: int, shape: tuple):
        rng = default_rng(seed)
        return rng.integers(0,256,size=shape,dtype=np.uint8)

    @staticmethod
    def sha256_hash_image(img: Image.Image, user_string: str):
        b = np.array(img).tobytes()
        return hashlib.sha256(b + user_string.encode()).hexdigest()

    @staticmethod
    def pick_random_pixels(img: np.ndarray, num_pixels=4):
        h,w,_ = img.shape
        pixels = []
        for _ in range(num_pixels):
            x,y = random.randrange(w), random.randrange(h)
            pixels.append((x,y,tuple(img[y,x])))
        return pixels

    @classmethod
    def encrypt(cls, img: Image.Image, user_string: str):
        arr = np.array(img.convert('RGB'),dtype=np.uint8)
        shape = arr.shape
        composite = f"{user_string}_F_P{shape[0]}x{shape[1]}x{shape[2]}"
        seed = cls.get_seed_from_string(composite)
        composite = f"{shape[0]}x{shape[1]}x{shape[2]}"
        noise = cls.generate_noise_from_seed(seed, shape)
        noisy = (arr.astype(int)+noise.astype(int))%256
        noisy = noisy.astype(np.uint8)
        pixels = cls.pick_random_pixels(noisy)
        composite += "_E_E" + "".join(f"_|{x}|{y}|{r}|{g}|{b}" for x,y,(r,g,b) in pixels)
        hsh = cls.sha256_hash_image(Image.fromarray(noisy), user_string)
        composite += f"_HASH_{hsh}"
        return noisy, noise, composite

    @classmethod
    def decrypt(cls, encrypted: np.ndarray, tkey: str, user_string: str):
        # verify hash
        expected = tkey.split("_HASH_")[1]
        actual = cls.sha256_hash_image(Image.fromarray(encrypted), user_string)
        if expected!=actual:
            raise ValueError("Integrity check failed")
        # verify shape
        shp = tkey.split("_E_E")[0]
        if shp!=f"{encrypted.shape[0]}x{encrypted.shape[1]}x{encrypted.shape[2]}":
            raise ValueError("Shape mismatch")
        # recreate noise & recover
        composite = f"{user_string}_F_P{shp}"
        seed = cls.get_seed_from_string(composite)
        noise = cls.generate_noise_from_seed(seed, encrypted.shape)
        recovered = (encrypted.astype(int)-noise.astype(int))%256
        return recovered.astype(np.uint8)
