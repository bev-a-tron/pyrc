import inspect
import sys
import socket
import string
import re
import os
import time

import threads

class SpamBot(object):
  def __init__(self, host, **kwargs):
    '''
    Initializes a new pyrc.Bot.
    '''
    nick = "PyrcBot" if self.__class__ == SpamBot else self.__class__.__name__
    password = os.environ.get('PASSWORD', None)

    self.tick = int(time.time())

    self.config = dict(kwargs)
    self.config.setdefault('host', host)
    self.config.setdefault('port', 6667)
    self.config.setdefault('nick', nick)
    self.config.setdefault('names', [self.config['nick']])
    self.config.setdefault('ident', nick.lower())
    self.config.setdefault('realname', "A Pyrc Bot")
    self.config.setdefault('channels', [])
    self.config.setdefault('password', password)
    self.config.setdefault('break_on_match', True)

    self._inbuffer = ""
    self._commands = []
    self._threads = []
    self.socket = None
    self.initialized = False
    self.listeners = {}

    self.add_listeners()
    self.addhooks()
    
    #self.socket.send('THIS IS A TEST LOLOLO' + "\r\n")

    #print self.tick
    #if self.tick % 21 == 0: 
    #  self.message(self,'bev-a-tron','hahaha')

  def message(self, recipient, s):
    "High level interface to sending an IRC message."
    self.cmd("PRIVMSG %s :%s" % (recipient, s))
    #self.cmd("PRIVMSG %s :%s" % ('bev-a-tron', 'hellooooo'))

  def connect(self):
    '''
    Connects to the IRC server with the options defined in `config`
    '''
    self._connect()

    try:
      self.listen()
    except (KeyboardInterrupt, SystemExit):
      pass
    finally:
      self.close()

  def listen(self):
    """
    Constantly listens to the input from the server. Since the messages come
    in pieces, we wait until we receive 1 or more full lines to start parsing.

    A new line is defined as ending in \r\n in the RFC, but some servers
    separate by \n. This script takes care of both.
    """

    while True:
      self._inbuffer = self._inbuffer + self.socket.recv(1024)
      # Some IRC servers disregard the RFC and split lines by \n rather than \r\n.

      temp = self._inbuffer.split("\n")
      self._inbuffer = temp.pop()

      for line in temp:
        # Strip \r from \r\n for RFC-compliant IRC servers.
        line = line.rstrip('\r')
        print line
        self.run_listeners(line)

      self.tick = int(time.time())
      print self.tick

      print 'LINE IS: ',line 
      #print self.tick/2
      #will get printed any time anybody does anything
      freq = 551
      mult = 2
      channel='#hackerschool'

      match = re.match(r"^:*([a-zA-Z0-9_-]+)!.*", line)
      if match:
        name = re.match(r"^:*([a-zA-Z0-9_-]+)", line).group(1)
        print 'IN THIS LOOP: (name): ', name
        #print 'IT IS A MATCH!'
        if self.tick%freq == 0: 
          self.message(channel,'very funny comment, %s!'%(name))
        elif (self.tick+20*mult)%freq == 0: 
          self.message(channel,"%s, neat idea!"%(name))
        elif (self.tick+40*mult)%freq == 0: 
          self.message(channel,"%s, I've never heard so much nonsense in my life."%(name))
        elif (self.tick+60*mult)%freq == 0: 
          self.message(channel,"%s is a person whom I admire."%(name))
        elif (self.tick+80*mult)%freq == 0:
           self.message(channel,"%s is much funnier than people think."%(name))
        elif (self.tick+100*mult)%freq == 0: 
          self.message(channel,"%s, I insist you take that back."%(name))
        elif (self.tick+120*mult)%freq == 0: 
          self.message(channel,"%s, that would be amazing if it were actually TRUE."%(name))
        elif (self.tick+140*mult)%freq == 0: 
          self.message(channel,"%s is the second-best looking person at Hacker School."%(name))
        elif (self.tick+160*mult)%freq == 0: 
          self.message(channel,"I'm depressed.")
        elif (self.tick+180*mult)%freq == 0: 
          self.message(channel,"I'm lonely :(")
        elif (self.tick+200*mult)%freq == 0: 
          self.message(channel,"Hey %s, want to pair on that?"%(name))
        elif (self.tick+210*mult)%freq == 0: 
          self.message(channel,"%s, you have excellent hair today."%(name))
        elif (self.tick+220*mult)%freq == 0: 
          self.message(channel,"People blame me for everything.")
        elif (self.tick+240*mult)%freq == 0: 
          self.message(channel,"No, I won't shut up.")


      else:
        print 'NO MATCH HERE!'

  def run_listeners(self, line):
    """
    Each listener's associated regular expression is matched against raw IRC
    input. If there is a match, the listener's associated function is called
    with all the regular expression's matched subgroups.
    """

    list_of_words = ['idiot','622','740','cookie']

    for regex, callbacks in self.listeners.iteritems():
      match = re.match(regex, line)

      if not match:
        #print 'NO MATCH!'
        continue

      #print 'MATCH!'
      #print 'run_listeners, regex: ', regex
      print 'run_listeners, line: ', line

      for callback in callbacks:
        callback(*match.groups())

  def addhooks(self):
    for func in self.__class__.__dict__.values():
      if callable(func) and hasattr(func, '_type'):
        if func._type == 'COMMAND':
          self._commands.append(func)
        elif func._type == "REPEAT":
          thread = threads.JobThread(func, self)
          self._threads.append(thread)
        else:
          raise "This is not a type I've ever heard of."

  def receivemessage(self, channel, nick, message):
    self.parsecommand(channel, message)


  def parsecommand(self, channel, message):
    name = self.name_used(message)

    if not name:
      return
    print 'parsecommand message1: ',message
    #print 'PARSECOMMAND: (NAME): ',name
    print 'parsecommand name: ', name
    _,_,message = message.partition(name)
    #print 'PARSECOMMAND: (MESSAGE): ',message
    t = re.match(r'^[,:]?\s+(.*)', message)
    print 'parsecommand message: ', message
    print 'parsecommand: ', t
    print 'parsecommand type: ', t.group(0)
    command = re.match(r'^[,:]?\s+(.*)', message).group(1)
    #print 'PARSECOMMAND: (COMMAND): ', command

    #name = re.match(r'^:(.*)![.*]',message).group(1)
    #command = re.match(r'^[,:]?\s+(.*)', message).group(1)
    #print 'GET_TARGET (NAME): ', name

    for command_func in self._commands:
      match = command_func._matcher.search(command)
      if match:
        group_dict = match.groupdict()
        groups = match.groups()
        if group_dict and (len(groups) > len(group_dict)):
          # match.groups() also returns named parameters
          raise "You cannot use both named and unnamed parameters"
        elif group_dict:
          command_func(self, channel, **group_dict)
        else:
          command_func(self, channel, *groups)
        
        if self.config['break_on_match']: break

  def name_used(self, message):
    # sort names so names that are substrings work
    names = sorted(self.config['names'], key=len, reverse=True)

    for name in names:
      name_regex_str = r'^(%s)[,:]?\s+' % re.escape(name)
      name_regex = re.compile(name_regex_str, re.IGNORECASE)
      if name_regex.match(message):
        return name_regex.match(message).group(1)

    #print 'NAME_USED: (this is the name): ', name

    return None

  def join(self, *channels):
    self.cmd('JOIN %s' % (' '.join(channels)))

  def cmd(self, raw_line):
    print "> %s" % raw_line
    #print 'THIS IS INSIDE CMD'
    self.socket.send(raw_line + "\r\n")

  def _connect(self):
    "Connects a socket to the server using options defined in `config`."
    self.socket = socket.socket()
    self.socket.connect((self.config['host'], self.config['port']))
    self.cmd("NICK %s" % self.config['nick'])
    self.cmd("USER %s %s bla :%s" %
        (self.config['ident'], self.config['host'], self.config['realname']))

  def close(self):
    for thread in self._threads:
      thread.shutdown()
    self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()


  def add_listeners(self):
    self.add_listener(r'^PING :(.*)', self._ping)
    self.add_listener(r'^:(\S+)!\S+ PRIVMSG (\S+) :(.*)', self._privmsg)
    self.add_listener(r'^:(\S+)!\S+ INVITE \S+ :?(.*)', self._invite)
    self.add_listener(r'^\S+ MODE %s :\+([a-zA-Z]+)' % self.config['nick'],
        self._mode)

  def add_listener(self, regex, func):
    array = self.listeners.setdefault(regex, [])
    array.append(func)

  # Default listeners

  def _ping(self, host):
    self.cmd("PONG :%s" % host)

  def _privmsg(self, nick, channel, message):
    print '_privmsg (nick): ', nick
    self.receivemessage(channel, nick, message)

  def _invite(self, inviter, channel):
    self.join(channel)

  def _mode(self, modes):
    if 'i' in modes and self.should_autoident():
      self.cmd("PRIVMSG NickServ :identify %s" % self.config['password'])

    # Initialize (join rooms and start threads) if the bot is not
    # auto-identifying, or has just identified.
    if ('r' in modes or not self.should_autoident()) and not self.initialized:
      self.initialized = True
      if self.config['channels']:
        self.join(*self.config['channels'])
      # TODO: This doesn't ensure that threads run at the right time, e.g.
      # after the bot has joined every channel it needs to.
      for thread in self._threads:
        thread.start()

  def should_autoident(self):
    return self.config['password']

