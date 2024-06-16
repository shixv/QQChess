import time
import tkinter as tk
import numpy as np
import win32gui
import subprocess
from threading import Thread
from PIL import ImageGrab, Image

    #棋子名称
    # 红方	    黑方	    字母	    相当于国际象棋中的棋子	    数字
    # 帅	        将	    K	    King(王)	                1
    # 仕	        士	    A	    Advisor(没有可比较的棋子)	2
    # 相	        象	    B	    Bishop(象)	            3
    # 马	        马	    N	    Knight(马)	            4
    # 车	        车	    R	    Rook(车)	                5
    # 炮	        炮	    C	    Cannon(没有可比较的棋子)	6
    # 兵	        卒	    P	    Pawn(兵)	                7

TITLE = "QQ新中国象棋"  #窗口标题
CB_LT_X = 241 #棋盘坐标(相对于窗口)
CB_LT_Y = 77
CB_RB_X = 754
CB_RB_Y = 647
SUB_LT_X = 13 #切片裁剪量
SUB_LT_Y = 16
SUB_RB_X = 13
SUB_RB_Y = 16

# 获取窗体坐标位置(左上)
def getGameWindowPosition(title):
    # FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名
    window = win32gui.FindWindow(None,title)
    # 没有定位到游戏窗体
    while not window:
        print('定位游戏窗体失败，5秒后重试...')
        time.sleep(5)
        window = win32gui.FindWindow(None,title)
    # 定位到游戏窗体
    win32gui.SetForegroundWindow(window) # 将窗体顶置
    pos = win32gui.GetWindowRect(window)
    print("定位到游戏窗体：" + str(pos))
    return pos

# 获取一张完整的屏幕截图
def getScreenImage():
    print('捕获屏幕截图...')
    scim = ImageGrab.grab()  # 屏幕截图，获取到的是Image类型对象
    return np.array(scim)

# 判断图像是否与已经在列表中的图像相同，如果是返回标号
def isImageExist(img,img_list):
    if(isinstance(img_list,list) == False):
        return len(img_list)
    for i in range(len(img_list)):
        b = np.subtract(img_list[i],img) # 图片数组进行比较，返回的是两个图片像素点差值的数组，
        if not np.any(b):   # 如果全部是0，说明两图片完全相同。
            return i
        else:
            continue
    return len(img_list)

#截图获取棋子特征
def getChessPieces(initCB = False): #参数为True时，重新生成棋子特征
    pos = getGameWindowPosition(TITLE)
    #time.sleep(2) #等待窗口置顶，调试用
    #获取截图
    window_image_nd = getScreenImage()[pos[1]:pos[3],pos[0]:pos[2]]
    #裁剪截图获取棋盘
    cb_image_nd = window_image_nd[CB_LT_Y:CB_RB_Y,CB_LT_X:CB_RB_X]
    #切割棋盘
    #在X轴方向上应当9等分,Y轴方向上为10等分
    cp_x = (CB_RB_X - CB_LT_X)//9
    cp_y = (CB_RB_Y - CB_LT_Y)//10

    cp_sub_x = cp_x - SUB_LT_X - SUB_RB_X;
    cp_sub_y = cp_y - SUB_LT_Y - SUB_RB_Y;

    #构造棋盘矩阵
    cb_mat = np.zeros((10,9))
    #FEN格式串
    str_fen = []
    
    if(initCB):
        cb_list = []
        for y in range(0,10):
            cb_x_list = []
            for x in range(0,9):
                cp_image_nd = cb_image_nd[y*cp_y+SUB_LT_Y:(y+1)*cp_y-SUB_RB_Y,x*cp_x+SUB_LT_X:(x+1)*cp_x-SUB_RB_X]
                cb_x_list.append(cp_image_nd)
            cb_list.append(np.hstack(cb_x_list))
        cb_nd = np.vstack(cb_list)
        #Image.fromarray(cb_nd).save('cb.bmp')
        #生成棋子图,假设局面为开局，红方在下
        #顺序 帅士相马车炮兵 红方在前
        cp_nd_list = []
        cp_nd_list.append(cb_nd[9*cp_sub_y:10*cp_sub_y,4*cp_sub_x:5*cp_sub_x]) 
        cp_nd_list.append(cb_nd[9*cp_sub_y:10*cp_sub_y,3*cp_sub_x:4*cp_sub_x]) 
        cp_nd_list.append(cb_nd[9*cp_sub_y:10*cp_sub_y,2*cp_sub_x:3*cp_sub_x]) 
        cp_nd_list.append(cb_nd[9*cp_sub_y:10*cp_sub_y,1*cp_sub_x:2*cp_sub_x]) 
        cp_nd_list.append(cb_nd[9*cp_sub_y:10*cp_sub_y,0*cp_sub_x:1*cp_sub_x]) 
        cp_nd_list.append(cb_nd[7*cp_sub_y:8*cp_sub_y,1*cp_sub_x:2*cp_sub_x]) 
        cp_nd_list.append(cb_nd[6*cp_sub_y:7*cp_sub_y,0*cp_sub_x:1*cp_sub_x]) 
        cp_nd_list.append(cb_nd[0*cp_sub_y:1*cp_sub_y,4*cp_sub_x:5*cp_sub_x]) 
        cp_nd_list.append(cb_nd[0*cp_sub_y:1*cp_sub_y,3*cp_sub_x:4*cp_sub_x]) 
        cp_nd_list.append(cb_nd[0*cp_sub_y:1*cp_sub_y,2*cp_sub_x:3*cp_sub_x]) 
        cp_nd_list.append(cb_nd[0*cp_sub_y:1*cp_sub_y,1*cp_sub_x:2*cp_sub_x]) 
        cp_nd_list.append(cb_nd[0*cp_sub_y:1*cp_sub_y,0*cp_sub_x:1*cp_sub_x]) 
        cp_nd_list.append(cb_nd[2*cp_sub_y:3*cp_sub_y,1*cp_sub_x:2*cp_sub_x]) 
        cp_nd_list.append(cb_nd[3*cp_sub_y:4*cp_sub_y,0*cp_sub_x:1*cp_sub_x]) 
        cp_nd = np.hstack(cp_nd_list)
        Image.fromarray(cp_nd).save('cp.bmp')
    else:
        #构造字符数组
        cp_name = 'KABNRCPkabnrcp+'
        #读取棋子
        cp_nd = np.array(Image.open('cp.bmp'))
        cp_list_nd = np.split(cp_nd,14,axis = 1)
        #空位计数器
        empty_cnt = 0
        #判断红黑
        turn = checkTurn(cb_image_nd[0*cp_y:3*cp_y,3*cp_x:6*cp_x],cp_list_nd[7])
        print('')
        for y in range(0,10):
            for x in range(0,9):
                cp_image_nd = cb_image_nd[y*cp_y+SUB_LT_Y:(y+1)*cp_y-SUB_RB_Y,x*cp_x+SUB_LT_X:(x+1)*cp_x-SUB_RB_X]
                idx = isImageExist(cp_image_nd,cp_list_nd);
                cb_mat[y,x] = idx
                print(cp_name[idx],end="")
                if(idx != 14):
                    if(empty_cnt != 0):
                        str_fen.append(str(empty_cnt))
                        empty_cnt = 0
                    str_fen.append(cp_name[idx])
                else:
                    empty_cnt+=1
            if(empty_cnt != 0):
                str_fen.append(str(empty_cnt))
                empty_cnt = 0
            str_fen.append('/')
            print('')
        str_fen = str_fen[:-1]
        str_fen.append(' ')
        if(turn):
            str_fen.append('w')
        else:
            str_fen.append('b')
        str_fen.append(' - - 0 1')
    return ''.join(str_fen)

#检测我方颜色
#输入的是上方将活动的9个点位,和黑将
#返回True说明是红方，False为黑方
def checkTurn(king_image_nd,cp_king_nd):
    cp_x = (CB_RB_X - CB_LT_X)//9
    cp_y = (CB_RB_Y - CB_LT_Y)//10
    for y in range(3):
        for x in range(3):
            b = np.subtract(king_image_nd[y*cp_y+SUB_LT_Y:(y+1)*cp_y-SUB_RB_Y,x*cp_x+SUB_LT_X:(x+1)*cp_x-SUB_RB_X],cp_king_nd)
            if not np.any(b):   # 如果全部是0，说明两图片完全相同。
                return True
    return False

def onDestroy():
    pf.stdin.write('quit\n'.encode())
    pf.stdin.flush()
    root_window.destroy()

def readOutput():
    while True:
        time.sleep(0.5)
        line = pf.stdout.readline().decode()
        label_output.config(text=line)


def run():
    str_fen = getChessPieces(False)
    print(str_fen)
    cmd_fen = 'position fen ' + str_fen + '\n'
    pf.stdin.write('ucinewgame\n'.encode())
    pf.stdin.write(cmd_fen.encode())
    pf.stdin.write('go depth 1\n'.encode())
    pf.stdin.flush()
                
if __name__ == '__main__':

    pf = subprocess.Popen("pikafish-proxy.exe",stdin=subprocess.PIPE,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    
    pf.stdin.write('ucci\n'.encode())
    pf.stdin.write('setoption usemillisec true\n'.encode())
    pf.stdin.write('setoption promotion false\n'.encode())
    pf.stdin.write('setoption hashsize 0'.encode())
    pf.stdin.write('setoption threads 0'.encode())
    pf.stdin.write('setoption idle none\n'.encode())
    pf.stdin.write('setoption randomness small\n'.encode())
    pf.stdin.write('setoption style normal\n'.encode())
    pf.stdin.write('setoption newgame\n'.encode())
    pf.stdin.write('setoption ponder true\n'.encode())
    pf.stdin.flush()

    root_window = tk.Tk()
    root_window.title('圆神')
    root_window.attributes("-topmost", True)
    root_window.protocol('WM_DELETE_WINDOW',onDestroy)
    
    btn_start = tk.Button(root_window,text='启动！',command=run)
    label_output = tk.Label(root_window,text='')
    btn_start.pack(side='left')
    label_output.pack(side='left')
    #创建线程，读取引擎的输出
    thread = Thread(target=readOutput,daemon=True)
    thread.start()

    root_window.mainloop()



