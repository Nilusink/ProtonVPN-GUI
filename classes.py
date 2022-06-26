from tkinter import *
# import typing as tp
# import numpy as np


# class Vec3:
#     """
#     Simple 3D vector class
#     """
#     x: float
#     y: float
#     z: float
#     angle_xy: float
#     angle_xz: float
#     length_xy: float
#     length: float
#
#     def __init__(self):
#         self.__x: float = 0
#         self.__y: float = 0
#         self.__z: float = 0
#         self.__angle_xy: float = 0
#         self.__angle_xz: float = 0
#         self.__length_xy: float = 0
#         self.__length: float = 0
#
#     @property
#     def x(self) -> float:
#         return self.__x
#
#     @x.setter
#     def x(self, value: float) -> None:
#         self.__x = value
#         self.__update("c")
#
#     @property
#     def y(self) -> float:
#         return self.__y
#
#     @y.setter
#     def y(self, value: float) -> None:
#         self.__y = value
#         self.__update("c")
#
#     @property
#     def z(self) -> float:
#         return self.__z
#
#     @z.setter
#     def z(self, value: float) -> None:
#         self.__z = value
#         self.__update("c")
#
#     @property
#     def cartesian(self) -> tp.Tuple[float, float, float]:
#         """
#         :return: x, y, z
#         """
#         return self.x, self.y, self.z
#
#     @cartesian.setter
#     def cartesian(self, value: tp.Tuple[float, float, float]) -> None:
#         """
#         :param value: (x, y, z)
#         """
#         self.__x, self.__y, self.__z = value
#         self.__update("c")
#
#     @property
#     def angle_xy(self) -> float:
#         return self.__angle_xy
#
#     @angle_xy.setter
#     def angle_xy(self, value: float) -> None:
#         self.__angle_xy = self.normalize_angle(value)
#         self.__update("p")
#
#     @property
#     def angle_xz(self) -> float:
#         return self.__angle_xz
#
#     @angle_xz.setter
#     def angle_xz(self, value: float) -> None:
#         self.__angle_xz = self.normalize_angle(value)
#         self.__update("p")
#
#     @property
#     def length_xy(self) -> float:
#         """
#         can't be set
#         """
#         return self.__length_xy
#
#     @property
#     def length(self) -> float:
#         return self.__length
#
#     @length.setter
#     def length(self, value: float) -> None:
#         self.__length = value
#         self.__update("p")
#
#     @property
#     def polar(self) -> tp.Tuple[float, float, float]:
#         """
#         :return: angle_xy, angle_xz, length
#         """
#         return self.angle_xy, self.angle_xz, self.length
#
#     @polar.setter
#     def polar(self, value: tp.Tuple[float, float, float]) -> None:
#         """
#         :param value: (angle_xy, angle_xz, length)
#         """
#         self.__angle_xy = self.normalize_angle(value[0])
#         self.__angle_xz = self.normalize_angle(value[1])
#         self.__length = value[2]
#         self.__update("p")
#
#     @staticmethod
#     def from_polar(angle_xy: float, angle_xz: float, length: float) -> "Vec3":
#         """
#         create a Vec3 from polar form
#         """
#         v = Vec3()
#         v.polar = angle_xy, angle_xz, length
#         return v
#
#     @staticmethod
#     def from_cartesian(x: float, y: float, z: float) -> "Vec3":
#         """
#         create a Vec3 from cartesian form
#         """
#         v = Vec3()
#         v.cartesian = x, y, z
#         return v
#
#     @classmethod
#     def from_lat_lon(cls, lat: float, lon: float) -> "Vec3":
#         c_t_p = (np.pi/180)
#         return cls.from_polar(angle_xy=lat*c_t_p, angle_xz=lon*c_t_p, length=1)
#
#     def split(self, direction: "Vec3") -> tp.Tuple["Vec3", "Vec3", "Vec3"]:
#         """
#         calculate the x, y and z components of length facing (angle1, angle2)
#         """
#         a = direction.angle_xy - self.angle_xy
#         b = direction.angle_xz - self.angle_xz
#         tmp = np.cos(a) * self.length
#         z = np.sin(a) * self.length
#         x = np.cos(b) * tmp
#         y = np.sin(b) * tmp
#
#         now_collision = Vec3.from_polar(
#             angle_xy=direction.angle_xy,
#             angle_xz=direction.angle_xz,
#             length=x
#         )
#
#         now_carry1 = Vec3.from_polar(
#             angle_xy=direction.angle_xy - np.pi / 2,
#             angle_xz=direction.angle_xz,
#             length=y
#         )
#
#         now_carry2 = Vec3.from_polar(
#             angle_xy=direction.angle_xy,
#             angle_xz=direction.angle_xz - np.pi / 2,
#             length=z
#         )
#
#         return now_collision, now_carry1, now_carry2
#
#     def cross(self, other: "Vec3") -> "Vec3":
#         x = self.y * other.z - self.z * other.y
#         y = self.z * other.x - self.x * other.z
#         z = self.x * other.y - self.y * other.x
#
#         return Vec3.from_cartesian(x, y, z)
#
#     @staticmethod
#     def normalize_angle(angle: float) -> float:
#         """
#         removes "overflow" from an angle
#         """
#         while angle > 2 * np.pi:
#             angle -= 2 * np.pi
#
#         while angle < -2 * np.pi:
#             angle += 2 * np.pi
#
#         return angle
#
#     def to_x_y(self) -> tuple[float, float]:
#         x = self.angle_xz / np.pi
#         # y = np.cos(np.pi / 2 - self.angle_xy)
#         y = 1 - np.sin(np.pi/2 - self.angle_xy)
#         return x, y
#
#     # maths
#     def __neg__(self) -> "Vec3":
#         self.cartesian = [-el for el in self.cartesian]
#         return self
#
#     def __add__(self, other) -> "Vec3":
#         if type(other) == Vec3:
#             return Vec3.from_cartesian(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)
#
#         return Vec3.from_cartesian(x=self.x + other, y=self.y + other, z=self.z + other)
#
#     def __sub__(self, other) -> "Vec3":
#         if type(other) == Vec3:
#             return Vec3.from_cartesian(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)
#
#         return Vec3.from_cartesian(x=self.x - other, y=self.y - other, z=self.z - other)
#
#     def __mul__(self, other) -> "Vec3":
#         if type(other) == Vec3:
#             return Vec3.from_polar(
#                 angle_xy=self.angle_xy + other.angle_xy,
#                 angle_xz=self.angle_xz + other.angle_xz,
#                 length=self.length * other.length
#             )
#
#         return Vec3.from_cartesian(x=self.x * other, y=self.y * other, z=self.z * other)
#
#     def __truediv__(self, other) -> "Vec3":
#         return Vec3.from_cartesian(x=self.x / other, y=self.y / other, z=self.z / other)
#
#     # internal functions
#     def __update(self, calc_from: str) -> None:
#         match calc_from:
#             case "p":
#                 self.__length_xy = np.cos(self.angle_xz) * self.length
#                 z = np.sin(self.angle_xz) * self.length
#                 x = np.cos(self.angle_xy) * self.__length_xy
#                 y = np.sin(self.angle_xy) * self.__length_xy
#                 self.__x = x
#                 self.__y = y
#                 self.__z = z
#
#             case "c":
#                 self.__length_xy = np.sqrt(self.y**2 + self.x**2)
#                 self.__angle_xy = np.arctan2(self.y, self.x)
#                 self.__angle_xz = np.arctan2(self.z, self.x)
#                 self.__length = np.sqrt(self.x**2 + self.y**2 + self.z**2)
#
#     def __repr__(self) -> str:
#         return f"<\n" \
#                f"\tVec3:\n" \
#                f"\tx:{self.x}\ty:{self.y}\tz:{self.z}\n" \
#                f"\tangle_xy:{self.angle_xy}\tangle_xz:{self.__angle_xz}\tlength:{self.length}\n" \
#                f">"


class ToolTip(object):

    def __init__(self, widget, text: str):
        self.tip_window = None
        self.widget = widget
        self.x = self.y = 0
        self.text = text
        self.id = None

        widget.bind("<Enter>", lambda *_e: self.showtip())
        widget.bind("<Leave>", lambda *_e: self.hidetip())

    def showtip(self,):
        """Display text in tooltip window"""
        if self.tip_window or not self.text:
            return

        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#292733", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
