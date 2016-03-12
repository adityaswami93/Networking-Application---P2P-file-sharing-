#!/usr/bin/python

import sys, getopt
import struct
import time
import os
from socket import *

port = 6789    #port no. is fixed
DATA_RATE = 4096
FILENAME_SEPARATOR = '0x00'

def make_svr_skt():
   curr_socket = socket(AF_INET,SOCK_STREAM)
   curr_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
   curr_socket.bind(('',port))
   return curr_socket

def make_client_skt(ip_addr):
   clientSocket = socket(AF_INET, SOCK_STREAM)
   clientSocket.connect((ip_addr,port))
   return clientSocket


def create_client(ip_addr,directory):
   client_socket = make_client_skt(ip_addr)
   #sentence = raw_input('Input lowercase sentence:')
   msgSent = 'clientready'
   client_socket.send(msgSent)
   file_exchange = []
   msgrcvd = client_socket.recv(1024)
   #client_socket.close()
   if msgrcvd == 'svrready':
      #client_socket.connect((ip_addr,port))
      file_list_client = get_file_list(directory)
      client_socket.send(file_list_client)
      common_files_str = client_socket.recv(1024)
      file_exchange = get_list_fileToTransfer(file_list_client,common_files_str)
      msgSent = 'sendingFile'
      client_socket.send(msgSent)
      msgrcvd = client_socket.recv(1024)
      print 'File to exchange', file_exchange
   if msgrcvd == 'sendOk':
      print('yes')
      send_files(client_socket,file_exchange,directory)
      #client_socket.settimeout(10)
      while(msgrcvd != 'sendingfiles'):
        try:
          msgrcvd = client_socket.recv(1024)
          print msgrcvd
        except error:
          continue
      else:
        client_socket.send('readytoreceive')
      rcv_files(client_socket,directory)

      # for filename in file_exchange:
      #   f = open(filename,'rb')
      #   l = f.read()
      #   data_size = len(l)
      #   data_sent = str(filename) + ' ' + str(data_size) + ' '
      #   while(len(data_sent)<1024):
      #     data_sent += ' '
      #   print filename
      #   client_socket.settimeout(5.0)
      #   client_socket.send(data_sent)
      #   print 'Sending...'
      #   client_socket.sendall(l)
      #   f.close()
   client_socket.close()
  
  
def create_svr(directory):
   curr_socket = make_svr_skt()
   curr_socket.listen(5)
   print 'server started'
   list_files = ""
   while True:
      connectionSocket, addr = curr_socket.accept()
      msg = connectionSocket.recv(1024)
      bytesrcvd = 0
      print(msg)
      if msg == 'clientready':
         msg = 'svrready'
         file_list_svr = get_file_list(directory)
         connectionSocket.send(msg)
         file_list_client = connectionSocket.recv(1024)
         common_files = get_list_commonfiles(file_list_client,file_list_svr)
         common_files_str = ''
         for filename in common_files:
            common_files_str += str(filename) + FILENAME_SEPARATOR
         connectionSocket.send(common_files_str)
         msg = connectionSocket.recv(1024)
         file_exchange = get_list_fileToTransfer(file_list_svr,common_files_str)
         print 'file_to_send' , file_exchange
         #connectionSocket.close()
      if msg == 'sendingFile':
        msg = 'sendOk'
        connectionSocket.send(msg)
        if rcv_files(connectionSocket,directory) == False:
          print('check')
          msg = 'sendingfiles'
          connectionSocket.send(msg)
        msg = connectionSocket.recv(1024)
        #rcv_files(connectionSocket,directory)
        #connectionSocket.settimeout(10)
      if msg == 'readytoreceive':
        if send_files(connectionSocket,file_exchange,directory):
          break
      connectionSocket.close()


def send_files(client_socket,file_exchange,directory):
  file_list_arr = []
  for (dirpath, dirnames, filenames) in os.walk(directory):
      for filename in file_exchange:
        if filename in filenames:
          file_list_arr.append([dirpath,filename])
  for fileinfo in file_list_arr:
    f = open(fileinfo[0]+'/'+fileinfo[1],'rb')
    l = f.read()
    data_size = len(l)
    data_sent = str(fileinfo[1]) + FILENAME_SEPARATOR + str(data_size)
    while(len(data_sent)<1024):
      data_sent += ' '
    print fileinfo[1]
    client_socket.settimeout(5.0)
    client_socket.send(data_sent)
    print 'Sending...'
    client_socket.sendall(l)
    f.close()
  client_socket.send('msgended')
  return True

def rcv_files(connectionSocket,directory):
  print 'The server is ready to receive'
  while True:
    data_rcvd = connectionSocket.recv(1024)
    if data_rcvd == 'msgended':
      return False
    if not data_rcvd:
      return False
    print 'data_rcvd', data_rcvd
    data_rcvd = data_rcvd.split(FILENAME_SEPARATOR)
    # if not len(data_rcvd):
    #   break;
    filename = data_rcvd[0]
    data_size = int(data_rcvd[1])
    f = open(directory+'/'+filename,'a+')
    if data_size<1024:
      l = connectionSocket.recv(data_size)
      f.write(l)
    else:
      while data_size > 1024:
        print 'Reciving..'
        l = connectionSocket.recv(1024)
        f.write(l)
        data_size -= 1024
      else:
        print 'last receive .'
        l = connectionSocket.recv(data_size)
        f.write(l)
    f.close()


def get_file_list(directory):
   file_list_arr = []
   list_files = ""
   if directory == '':
    directory = '.'
   for (dirpath, dirnames, filenames) in os.walk(directory):
      file_list_arr.extend(filenames)
   file_list_arr = sorted(file_list_arr,key=str.lower)
   for filename in file_list_arr:
      list_files += str(filename) + FILENAME_SEPARATOR
   return list_files

def get_list_fileToTransfer(file_list,common_files):
   common_files = common_files.split(FILENAME_SEPARATOR)
   file_list = file_list.split(FILENAME_SEPARATOR)
   exchange_file = []
   for filename in file_list:
      if filename not in common_files:
         exchange_file.append(filename)
   return exchange_file

def get_list_commonfiles(client_files,svr_files):
   client_files = client_files.split(FILENAME_SEPARATOR)
   svr_files = svr_files.split(FILENAME_SEPARATOR)
   return set(client_files) & set(svr_files)

def main(argv):
   ip_addr = ''
   directory = ''
   try:
      opts, args = getopt.getopt(argv,"hi:d:",["help","ipaddr=","dir="])
   except getopt.GetoptError:
      print 'python.py -i <ip addr> -d <dir>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'python.py -i <ip addr> -d <dir>'
         sys.exit()
      elif opt in ("-i", "--ipaddr"):
         ip_addr = arg
      elif opt in ("-d", "--dir"):
         directory = arg
   print 'ipaddr is "', ip_addr
   print 'dir is "', directory

   if str(ip_addr)=="":
      create_svr(directory)
   else:
      create_client(ip_addr,directory)




if __name__ == "__main__":
   main(sys.argv[1:])