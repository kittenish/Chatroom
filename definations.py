# -*- coding: utf-8 -*-
# coding="utf-8"
import sys
reload(sys)
sys.setdefaultencoding('utf8')

MESSAGE = (0)
MEMBER = (1)
ADDMEMBER = (2)
REFRESH_MEMBER = (3)
CLIENT = (4)
INFO = (5)
JOIN = (6)
GET_MEMBER = (7)
LEAVE_ROOM = (8)
GET_LOG = (9)
SAVE_LOG = (10)
ADD_FILE = (11)
GET_FILE = (12)
DOWNLOAD = (13)

'''
传输格式：
（1）传输消息：

	整体格式为：length + { type : value, key1 : value1, key2 : value2, … , check : value }
	length ( 32 字节 ) : 全部信息长度。由于socket传输会把较小的信息合并传输，因此length用于在接受信息端按照长度依次接受信息。
	type ：消息格式的定义在 definations.py 中定义，根据不同的类型客户端和服务器端做不同的处理。
	key : value 键值对 ：信息内容。
	check ( 32 字节 ) : 校验和，计算信息部分的哈希值。在每一次接受信息之后，重新计算校验和，检测校验和是否和传输过来的check的值一致，
                       如果一致继续执行，否则则认为传输错误。

（2）传输文件：

	整体格式为 : length + fhead + content
	length ( 32 字节 ) : length = 0。服务器判断得到接下来传输的是文件，要按照fhead的内容进行解析。
	fhead : 调用 struct.pack 进行打包，获得文件基本信息（文件名，文件大小等），接收端通过 unpack 获得文件基本信息，之后接收文件。
	content : 使用文件打开 open 函数，以每1024个字节为单位传输。

'''
