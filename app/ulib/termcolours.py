# termcolours.py

"""***
Optional support for printing to the terminal in multiple colurs

***"""

#---------------------------------------------------------------------

class TermColours:
   BLACK   = chr(27) + "[0;30m"
   RED     = chr(27) + "[0;31m"
   GREEN   = chr(27) + "[0;32m"
   BLUE    = chr(27) + "[0;34m"
   MAGENTA = chr(27) + "[0;35m"
   
   RED_ON_GREY = chr(27) + "[47;31m"
   LRED_ON_GREY = chr(27) + "[1;47;31m"
   BLACK_ON_RED = chr(27) + "[41;30m"
   BLACK_ON_GREY = chr(27) + "[47;30m"
   BLUE_ON_GREY = chr(27) + "[47;34m"
   YELLOW_ON_RED =  chr(27) + "[1;47;30m"
   GREY_ON_WHITE = chr(27) + "[48;37m"
   DGREY_ON_WHITE = chr(27) + "[1;48;30m"
   LCYAN_ON_BLUE = chr(27) + "[1;44;36m"
   
   NORMAL = chr(27) + "[0m"
   BOLD = chr(27) + "[1m"
   FAINT = chr(27) + "[2m"
   UNDERLINE = chr(27) + "[4m"


def prColours():
   bgCol = range(30,50) 
   fgCol = range(30,50)
   for bg in bgCol:
      for fg in fgCol:
         seq = "[%d;%dm" % (bg, fg)
         escSeq = chr(27) + seq + seq + chr(27) + "[0;30m"
         print escSeq,
         if fg==39: print
      print
   for i in range(0,8):   
      seq = "[%dm" % i
      print TermColours.NORMAL + chr(27) + seq + " " + seq
   print TermColours.NORMAL 
      
class NullColours:
   BLACK   = ''
   RED     = ''
   GREEN   = ''
   BLUE    = ''
   MAGENTA = ''
   RED_ON_GREY = ''
   LRED_ON_GREY = ''
   BLACK_ON_RED = ''
   BLACK_ON_GREY = ''
   BLUE_ON_GREY = ''
   YELLOW_ON_RED =  ''
   GREY_ON_WHITE = ''
   DGREY_ON_WHITE = ''
   LCYAN_ON_BLUE = ''

tc = TermColours()
#tc = NullColours()

class Markup(TermColours):
   NORMAL = tc.BLACK
   SM = tc.BLUE
   ADDR = tc.GREEN
   #ADDR = chr(27) + "[46;34m"
   #ADDR = tc.BLUE_ON_GREY
   TREE = tc.BLACK
   TREE_TITLE = tc.BLUE_ON_GREY
   LLSC = tc.BLUE_ON_GREY
   #LLSC = tc.BLUE_ON_GREY
   LLSC_LVAL = tc.MAGENTA
   
#---------------------------------------------------------------------
   
if __name__=="__main__":   
   mu = Markup()
   print mu.NORMAL + "normal " + mu.SM + "#(1 2 55 $nil) " + mu.ADDR + "addr"  
   print "red or black???" 
   prColours()
   print TermColours.BOLD + "should be bold"
   
   print TermColours.NORMAL + "back to normal"


#end
