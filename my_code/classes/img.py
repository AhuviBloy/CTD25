# from __future__ import annotations
# import pathlib
# import cv2
# import numpy as np

# class Img:
#     def __init__(self):
#         self.img = None

#     def read(self, path: str | pathlib.Path,
#              size: tuple[int, int] | None = None,
#              keep_aspect: bool = False,
#              interpolation: int = cv2.INTER_AREA) -> Img:
#         path = str(path)
#         self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
#         if self.img is None:
#             raise FileNotFoundError(f"Cannot load image: {path}")

#         if size is not None:
#             target_w, target_h = size
#             h, w = self.img.shape[:2]

#             if keep_aspect:
#                 scale = min(target_w / w, target_h / h)
#                 new_w, new_h = int(w * scale), int(h * scale)
#             else:
#                 new_w, new_h = target_w, target_h

#             self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

#         return self

#     def draw_on(self, other_img: Img, x: int, y: int) -> None:
#         if self.img is None or other_img.img is None:
#             raise ValueError("Both images must be loaded before drawing.")

#         src = self.img
#         dst = other_img.img

#         if src.shape[2] != dst.shape[2]:
#             if src.shape[2] == 3 and dst.shape[2] == 4:
#                 src = cv2.cvtColor(src, cv2.COLOR_BGR2BGRA)
#             elif src.shape[2] == 4 and dst.shape[2] == 3:
#                 src = cv2.cvtColor(src, cv2.COLOR_BGRA2BGR)

#         h, w = src.shape[:2]
#         H, W = dst.shape[:2]

#         if y + h > H or x + w > W:
#             raise ValueError("Source image does not fit at the specified position.")

#         roi = dst[y:y + h, x:x + w]

#         if src.shape[2] == 4:
#             # Handle transparency (alpha channel)
#             alpha = src[:, :, 3] / 255.0
#             for c in range(3):
#                 roi[..., c] = (1 - alpha) * roi[..., c] + alpha * src[..., c]
#         else:
#             roi[:, :] = src

#         other_img.img[y:y + h, x:x + w] = roi

#     def put_text(self, txt: str, x: int, y: int, font_size: float,
#                  color=(255, 255, 255, 255), thickness: int = 1) -> None:
#         if self.img is None:
#             raise ValueError("Image not loaded.")
#         cv2.putText(self.img, txt, (x, y),
#                     cv2.FONT_HERSHEY_SIMPLEX, font_size,
#                     color, thickness, cv2.LINE_AA)

#     def show(self, winname: str = "Image") -> None:
#         if self.img is None:
#             raise ValueError("Image not loaded.")
#         cv2.imshow(winname, self.img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

#     def save(self, path: str | pathlib.Path) -> None:
#         """Save the current image to file."""
#         if self.img is None:
#             raise ValueError("Image not loaded.")
#         cv2.imwrite(str(path), self.img)


















# # from __future__ import annotations

# # import pathlib

# # import cv2
# # import numpy as np

# # class Img:
# #     def __init__(self):
# #         self.img = None

# #     def read(self, path: str | pathlib.Path,
# #              size: tuple[int, int] | None = None,
# #              keep_aspect: bool = False,
# #              interpolation: int = cv2.INTER_AREA) -> "Img":
# #         """
# #         Load `path` into self.img and **optionally resize**.

# #         Parameters
# #         ----------
# #         path : str | Path
# #             Image file to load.
# #         size : (width, height) | None
# #             Target size in pixels.  If None, keep original.
# #         keep_aspect : bool
# #             • False  → resize exactly to `size`
# #             • True   → shrink so the *longer* side fits `size` while
# #                        preserving aspect ratio (no cropping).
# #         interpolation : OpenCV flag
# #             E.g.  `cv2.INTER_AREA` for shrink, `cv2.INTER_LINEAR` for enlarge.

# #         Returns
# #         -------
# #         Img
# #             `self`, so you can chain:  `sprite = Img().read("foo.png", (64,64))`
# #         """
# #         path = str(path)
# #         self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
# #         if self.img is None:
# #             raise FileNotFoundError(f"Cannot load image: {path}")

# #         if size is not None:
# #             target_w, target_h = size
# #             h, w = self.img.shape[:2]

# #             if keep_aspect:
# #                 scale = min(target_w / w, target_h / h)
# #                 new_w, new_h = int(w * scale), int(h * scale)
# #             else:
# #                 new_w, new_h = target_w, target_h

# #             self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

# #         return self

# #     def draw_on(self, other_img, x, y):
# #         if self.img is None or other_img.img is None:
# #             raise ValueError("Both images must be loaded before drawing.")

# #         if self.img.shape[2] != other_img.img.shape[2]:
# #             if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
# #                 self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
# #             elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
# #                 self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

# #         h, w = self.img.shape[:2]
# #         H, W = other_img.img.shape[:2]

# #         if y + h > H or x + w > W:
# #             raise ValueError("Logo does not fit at the specified position.")

# #         roi = other_img.img[y:y + h, x:x + w]

# #         if self.img.shape[2] == 4:
# #             b, g, r, a = cv2.split(self.img)
# #             mask = a / 255.0
# #             for c in range(3):
# #                 roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
# #         else:
# #             other_img.img[y:y + h, x:x + w] = self.img

# #     def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
# #         if self.img is None:
# #             raise ValueError("Image not loaded.")
# #         cv2.putText(self.img, txt, (x, y),
# #                     cv2.FONT_HERSHEY_SIMPLEX, font_size,
# #                     color, thickness, cv2.LINE_AA)

# #     def show(self):
# #         if self.img is None:
# #             raise ValueError("Image not loaded.")
# #         cv2.imshow("Image", self.img)
# #         cv2.waitKey(0)
# #         cv2.destroyAllWindows()
















from __future__ import annotations
import pathlib, cv2, numpy as np

class Img:
    def __init__(self, mat: np.ndarray | None = None):
        self.img = mat            # אפשר לקבל מטריצה ישירות

    # ----------  קריאה מקובץ  ----------
    @classmethod
    def read(cls, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        mat = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if mat is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size:
            target_w, target_h = size
            h, w = mat.shape[:2]
            if keep_aspect:
                ratio = min(target_w/w, target_h/h)
                mat = cv2.resize(mat, (int(w*ratio), int(h*ratio)), interpolation)
            else:
                mat = cv2.resize(mat, (target_w, target_h), interpolation)
        return cls(mat)

    # ----------  ציור על תמונה אחרת  ----------
    def draw_on(self, other: "Img", x: int, y: int) -> None:
        if self.img is None or other.img is None:
            raise ValueError("Images not loaded")

        h, w = self.img.shape[:2]
        roi = other.img[y:y+h, x:x+w]

        src = self.img
        dst = roi

        if src.shape[2] == 4:                          # מקור עם Alpha
            alpha = src[:, :, 3:4] / 255.0
            dst[:, :, :3] = alpha * src[:, :, :3] + (1 - alpha) * dst[:, :, :3]
        elif src.shape[2] == 3 and dst.shape[2] == 4:  # מקור RGB → יעד RGBA
            dst[:, :, :3] = src                        # מעתיקים רק RGB
        else:                                          # RGB→RGB או RGBA→RGBA
            dst[:] = src

    # ----------  אקסטרות  ----------
    def put_text(self, txt, x, y, font_size,
                 color=(255,255,255,255), thickness=1):
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    def show(self, win="Image"):
        cv2.imshow(win, self.img); cv2.waitKey(0); cv2.destroyAllWindows()

    def save(self, path): cv2.imwrite(str(path), self.img)

    def copy(self):
        return Img(self.img.copy())

    def overlay(self, overlay_img, x, y, alpha=0.5):
        if overlay_img.img.shape[2] == 4:  # RGBA
            alpha_channel = overlay_img.img[:, :, 3] / 255.0 * alpha
            for c in range(3):
                self.img[y:y+overlay_img.img.shape[0], x:x+overlay_img.img.shape[1], c] = \
                    (alpha_channel * overlay_img.img[:, :, c] +
                    (1 - alpha_channel) * self.img[y:y+overlay_img.img.shape[0], x:x+overlay_img.img.shape[1], c])

    def resize(self, size):
        self.img = cv2.resize(self.img, size)
        return self

