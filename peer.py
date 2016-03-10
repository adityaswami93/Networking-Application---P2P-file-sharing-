#!/usr/bin/python

import sys, getopt
import os
from socket import *

port = 6789    #port no. is fixed

def make_svr_skt():
   curr_socket = socket(AF_INET,SOCK_STREAM)
   curr_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
   curr_socket.bind(('',port))
   return curr_socket

def make_client_skt(ip_addr):
   clientSocket = socket(AF_INET, SOCK_STREAM)
   clientSocket.connect((ip_addr,port))
   return clientSocket


def create_client(ip_addr):
   client_socket = make_client_skt(ip_addr)
   #sentence = raw_input('Input lowercase sentence:')
   msg = 'clientready'
   client_socket.send(msg)
   msgrcvd = client_socket.recv(1024)
   #client_socket.close()
   if msgrcvd == 'svrready':
      #client_socket.connect((ip_addr,port))
      file_list_client = get_file_list()
      client_socket.send(file_list_client)
      common_files_str = client_socket.recv(1024)
      client_socket.close()
      file_exchange = get_list_fileToTransfer(file_list_client,common_files_str)
      print 'File to exchange', file_exchange
   # else: error handling
   


   # file_list_svr = client_socket.recv(1024)
   # file_list_client = get_file_list()
   # #file_exchange = get_list_fileToTransfer(file_list_client,file_list_svr)
   # common_files = get_list_commonfiles(file_list_client,file_list_svr)
   # msg = 'commonfiles'
   # client_socket.send(msg)
   # msg = client_socket.recv(1024)
   # if msg == 'svrready':
   #    common_files_str = ''
   #    for filename in common_files:
   #       common_files_str += str(filename) + ' '
   #    client_socket.send(common_files_str)
   #    file_exchange = get_list_fileToTransfer(file_list_client,common_files_str)
   # #print 'From Server:', file_list_svr
   # print 'File to exchange', file_exchange
   # client_socket.close()

   

def create_svr():
   curr_socket = make_svr_skt()
   curr_socket.listen(1)
   print 'The server is ready to receive'
   list_files = ""
   while True:
      connectionSocket, addr = curr_socket.accept()
      msg = connectionSocket.recv(1024)
      print(msg)
      if msg == 'clientready':
         msg = 'svrready'
         file_list_svr = get_file_list()
         connectionSocket.send(msg)
         file_list_client = connectionSocket.recv(1024)
         common_files = get_list_commonfiles(file_list_client,file_list_svr)
         common_files_str = ''
         for filename in common_files:
            common_files_str += str(filename) + ' '
         connectionSocket.send(common_files_str)
         file_exchange = get_list_fileToTransfer(file_list_svr,common_files_str)
         print 'file_to_send' , file_exchange
         connectionSocket.close()


      # if msg == 'commonfiles':
      #    connectionSocket.send('svrready')
      #    common_files = connectionSocket.recv(1024)
      #    file_exchange = get_list_fileToTransfer(file_to_send,common_files)
      #    print 'file_to_send' , file_exchange
      #capitalizedSentence = sentence.upper()
      #connectionSocket.close()
   


def get_file_list():
   file_list_arr = []
   list_files = ""
   for (dirpath, dirnames, filenames) in os.walk('.'):
      file_list_arr.extend(filenames)
   file_list_arr = sorted(file_list_arr,key=str.lower)
   for filename in file_list_arr:
      list_files += str(filename) + ' '
   return list_files

def get_list_fileToTransfer(file_list,common_files):
   common_files = common_files.split()
   file_list = file_list.split()
   exchange_file = []
   for filename in file_list:
      if filename not in common_files:
         exchange_file.append(filename)
   return exchange_file

def get_list_commonfiles(client_files,svr_files):
   client_files = client_files.split()
   svr_files = svr_files.split()
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
      create_svr()
   else:
      create_client(ip_addr)




if __name__ == "__main__":
   main(sys.argv[1:])