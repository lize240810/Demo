import os
import io

import requests
from PIL import Image


def tk_show_image(img):
    '''
    使用tkinter显示图片
    '''
    import tkinter
    from PIL import ImageTk
    
    # root = tkinter.Toplevel()
    root = tkinter.Tk()
    img_tk = ImageTk.PhotoImage(img)
    frame = tkinter.Frame(master=root, width=img.width, height=img.height)
    frame.pack()
    canvas = tkinter.Canvas(master=frame, bg='#FFFFFF', width=img.width, height=img.height)
    canvas.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    canvas.create_image(0, 0, anchor=tkinter.NW, image=img_tk)
    root.update()
    tkinter.mainloop()


url = 'http://www.cqzuxia.com/static/images/newindex/logo.png'
# url = 'http://www.cqzuxia.com/uploads/170731/zsjz.jpg'
resp = requests.get(url)
if resp.ok:
    '''
    with open('zuxia-logo.png', 'wb') as f:
        f.write(resp.content)
    full_path = os.path.abspath('zuxia-logo.png')
    os.system('explorer {0}'.format(full_path))
    '''

    img = Image.open(io.BytesIO(resp.content))
    img.show()  # PIL显示方式（PNG显示失败）
    tk_show_image(img)  # TK显示方式（PNG显示成功）
    img.close()

    # os.remove(full_path)
else:
    print('请求失败')
