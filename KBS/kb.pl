:- dynamic position/4.
:- dynamic carrots.

0 :- carrots.

action(throw) :- carrots > 0.
%TODO: it is currently unused