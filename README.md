# jptest
A kivy example for Japanese alphabet

Help:
1. system commands: help, exit, setup, ...
   * help: it comes to this page
   * exit: close the window
   * setup: you would be able to see a textinput box:
   
         Time | Alphabet | Mode | Cheat | Speed | FontSize | Delay | Flakes:
           60,       0,      0,      1,      1,      30,       5,       6

       - Time: 1-n => the certain time, see Mode 0
       - Alphabet:  0 => hiragana   1 => katakana   2 => kanji
                   -1 => load the user-defined map from ~/jp_ext.map
       - Mode:  0 => count the character numbers in a certain time
                1 => count the time after you finish all characters
                2 => shot all before any flakes touch the buttom
       - Cheat: 0 => disable the prompt by clicking the flakes
                1 => enable the prompt by clicking the flakes
       - Speed: 1-n => flakes fall faster as the value gets bigger
       - FontSize: 1-n => the FontSize on each flake
       - Delay: 0 => no animation delay, shoot extremly fast
                1-n => the animation duration for shooting
       - Flakes:1-n => the numbers of the Flakes
    * ...: others would be matched with the flakes
2. clicks: on-flakes, on-bullet
     * on-flakes: show the prompt if Cheat is enable
     * on-bullet: it comes to this page, as help cmd does

Copyright:
1. Powered By : Xin Long <lucein.xin@gmail.com>  
2. Source Code : https://github.com/lxin/jptest
