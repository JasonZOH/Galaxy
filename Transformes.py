def transforme(self, x, y):
    #return self.transforme_2d(x, y)
    return self.transforme_perpective(x, y)


def transforme_2d(self, x, y):
    return int(x), int(y)


def transforme_perpective(self, x, y):
    ln_y = y * self.perspectiv_py / self.height
    if ln_y > self.perspectiv_py:
        ln_y = self.perspectiv_py
    diff_x = x - self.perspectiv_px
    diff_y = self.perspectiv_py - ln_y
    factor_y = diff_y / self.perspectiv_py
    factor_y = pow(factor_y, 4)

    offset = diff_x * factor_y

    tr_x = self.perspectiv_px + offset
    tr_y = self.perspectiv_py - factor_y * self.perspectiv_py
    return int(tr_x), int(tr_y)