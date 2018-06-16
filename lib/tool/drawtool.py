from tkinter import *
import time
import threading


class draw_function:
    font_config = ('times', 20, )

    def __init__(self, canvas_width, canvas_height, bd):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.master = Tk()
        self.master.title("Draw your own prosperity function")
        self.pre_x = -1
        self.pre_y = -1
        self.bd = bd
        self.w = Canvas(self.master,
                        bd=self.bd,
                        width=self.canvas_width,
                        height=self.canvas_height)
        self.w.pack(expand=YES, fill=BOTH)
        obj2 = self.w.create_text(
            self.canvas_width - self.bd, self.canvas_height + self.bd / 2, font=self.font_config, text='Done!')
        obj1 = self.w.create_text(self.canvas_width - self.bd * 10,
                                  self.canvas_height + self.bd / 2, font=self.font_config, text='Reset')
        self.w.bind("<B1-Motion>", self.paint)
        self.w.bind("<ButtonRelease-1>", self.release)
        self.w.tag_bind(obj2, '<Double-1>', self.sent_data)
        self.w.tag_bind(obj1, '<Double-1>', self.clearcanvas)
        self.w.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                offset=str(self.bd) + ',' + str(self.bd), fill='white', outline="")
        self.data = []

        t = threading.Thread(target=self.master.mainloop(), daemon=True)

        t.start()
        t.join()
        self.master.destroy()

    def sent_data(self, event):
        print("****Sent your draw****")
        self.master.quit()
        # self.master.destroy()
        return
        # master.quit()

    def clearcanvas(self, event):
        print('clear')
        self.w.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                offset=str(self.bd) + ',' + str(self.bd), fill='white', outline="")
        self.data = []

    def release(self, event):
        self.pre_x = self.pre_y = -1

    def paint(self, event):
        python_green = "#476042"
        #print(event.x, event.y)
        global pre_x, pre_y
        if self.pre_x == -1:
            self.pre_x = event.x
        if self.pre_y == -1:
            self.pre_y = event.y
        self.data.append([event.x, event.y])
        '''
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        w.create_oval(x1, y1, x2, y2, fill=python_green)
        '''
        self.w.create_line(self.pre_x, self.pre_y, event.x,
                           event.y, fill=python_green)
        self.pre_x, self.pre_y = event.x, event.y

if __name__ == '__main__':
    k = draw_pros()
    print(k.data)
    while(1):
        time.sleep(0.01)
