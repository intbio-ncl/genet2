from PIL import Image, ImageDraw, ImageFont
import re

start_val = (0,90,75)
hue_step = 20
sat_mod = 0.8
light_mod = 0.8
max_hue = 340
min_sat = 20
min_light = 18

class ColorPicker:
    def __init__(self,shuffle=True):
        self._colors = self._build_color(shuffle)

    def __iter__(self):
        for col in self._flatten():
            yield str(col)

    def __getitem__(self,index):
        try:
            return str(self._flatten()[index])
        except IndexError:
            return str(self._flatten()[-1])

    def increase_shade(self,hsl_val):
        hsl = HSLVal.parse(hsl_val)
        s = int(hsl.s * sat_mod)
        l = int(hsl.l * light_mod)
        if s < min_sat and l < min_light:
            s = start_val[1]
            l = start_val[2]
        hsl.s = s
        hsl.l = l
        return str(hsl)
    
    

    def produce_plot(self,outname):
        hsl_list = self._colors[0:int(len(self._colors)/4)]
        if isinstance(hsl_list[0],HSLVal):
            hsl_list = [[hsv_val] for hsv_val in hsl_list]
        grid_width = len(hsl_list) * 1000
        grid_height = len(max(hsl_list,key=len)) * 1000
        square_h = grid_height / len(max(hsl_list,key=len))
        square_l = grid_width / len(hsl_list)
        x_orig = 0
        y_orig = 0
        cur_x = x_orig
        cur_y = y_orig
        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 100)
        img = Image.new('RGB', (grid_width, grid_height), color = (255,255,255))
        d = ImageDraw.Draw(img)
        for color in hsl_list:
            cur_y = y_orig
            for shade in color:
                d.rectangle((cur_x, cur_y, cur_x + square_l, cur_y + square_h), fill=str(shade), outline=(255, 255, 255))
                d.text((cur_x,cur_y), str(shade), font=fnt,fill=(0,0,0))
                cur_y += square_h
            cur_x += square_l
        img.save(outname)
        return outname

    def _build_color(self,shuffle=True):
        cur_hue = start_val[0]
        hsl_list = []
        while cur_hue <= max_hue:
            cur_sat = start_val[1]
            cur_light = start_val[2]
            color_list = []
            while cur_sat > min_sat and cur_light > min_light:
                hsl_val = HSLVal(cur_hue,cur_sat,cur_light)
                color_list.append(hsl_val)
                cur_sat = int(cur_sat * sat_mod)
                cur_light = int(cur_light * light_mod)
            cur_hue += hue_step
            hsl_list.append(color_list)

        if shuffle:
            hsl_list = self._determinable_shuffle(hsl_list)
        return hsl_list

    def _determinable_shuffle(self,hsl_list):
        '''
        Only shuffle whole columns or whole rows.
        '''
        num_cols = len(hsl_list)
        # Swap each pair of rows index (0,1 - 2,3 - 4,5 ...)
        num_rows = len(max(hsl_list,key=len))
        next_row_i = 1
        while next_row_i < num_rows:
            hsl_list = self._swap_columns(hsl_list,next_row_i-1,next_row_i)
            next_row_i +=2

        # Move Columns based on odd|even and away from centre.
        # Ensures not only most distinct neigbours but also index 0 and 1 are 
        # most distinct as they are most used colors.
        mid_val = int(num_cols/2)
        # From middle column, 
        new_hsl_list = [hsl_list[mid_val]]
        # Add each odd column left
        new_hsl_list += hsl_list[1:mid_val:2]
        # Add each even column right.
        new_hsl_list += hsl_list[mid_val+2::2]
        # Add each odd column right.
        new_hsl_list += hsl_list[mid_val+1::2]
        # Add each even column left.
        new_hsl_list += hsl_list[0:mid_val:2]

        return new_hsl_list

    def _swap_columns(self,hsl_list, pos1, pos2):
        for item in hsl_list:
            item[pos1], item[pos2] = item[pos2], item[pos1]
        return hsl_list
        
    def _flatten(self):
        '''
        Flatterns row by row.
        '''
        flat_list = []
        for col in range(0,len(max(self._colors,key=len))): 
            for row in range(0,len(self._colors)):
                flat_list.append(self._colors[row][col])
        return flat_list

class HSLVal:
    def __init__(self,h,s,l):
        self.h = int(h)
        self.s = int(s)
        self.l = int(l)

    @classmethod
    def parse(cls,hsl):
        m=re.match("^\s*(\w+)\s*\((.*)\)",hsl)
        values = m.group(2).replace("%","")
        return cls(*values.split(","))

    def __repr__(self):
        return f'hsl({self.h},{self.s}%,{self.l}%)'

