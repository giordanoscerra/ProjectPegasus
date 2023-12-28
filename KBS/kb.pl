:- dynamic wounded_legs/1, hallucinating/1, blind/1, telepathic/1, punished/1, trapped/1, wearing/2, rusty/1, corroded/1.
:- dynamic confused/1, fumbling/1, slippery_fingers/1.
:- dynamic hostile/1.
:- dynamic stepping_on/3.
:- dynamic position/4.
:- dynamic action_count/2.
:- dynamic tameness/2.
:- dynamic carrots/1.
:- dynamic saddles/1.
:- dynamic riding/2. % riding(agent, steed), assert it when mounting, retract it when dismounting/slipping etc.
:- dynamic burdened/1, stressed/1, strained/1, overtaxed/1, overloaded/1.

% To translate into Prolog:
% Chance of succeeding a mounting action is: 5 * (exp level + steed tameness)
% cannot attempt to mount a steed if any of the following conditions apply:
% 
%     You are already riding.
%     You are hallucinating.
%     Your have wounded legs.
%     Your encumbrance is stressed or worse.
%     You are blind and not telepathic.
%     You are punished.
%     You or your steed are trapped.
%     You are levitating and cannot come down at will.
%     You are wearing rusty or corroded body armor.
rideable(X) :- is_steed(X), \+ riding(agent,_), \+ hallucinating(agent), \+ wounded_legs(agent), \+ encumbered(agent), \+ (blind(agent), \+ telepathic(agent)), \+ punished(agent)
    , \+ trapped(agent), \+ (wearing(agent, Y), (rusty(Y); corroded(Y))). % I do not intend to implement everything but we can do what we can in the time we have, as a flex

% You will always fail and slip if any of the following apply:[3]
% 
%     You are confused.
%     You are fumbling.
%     You have slippery fingers.
%     Your steed's saddle is cursed.
slippery :- confused(agent); fumbling(agent); slippery_fingers(agent). % WHAT IF THE SADDLE IS CURSED??????

unencumbered(agent) :- \+ burdened(agent), \+ stressed(agent), \+ strained(agent), \+ overtaxed(agent), \+ overloaded(agent).
encumbered(agent) :- stressed(agent); strained(agent); overtaxed(agent); overloaded(agent).

%%% GENERAL SUBTASKS feel free to add other conditions or comments to suggest them
action(getCarrot) :- 
    carrots(X), X == 0, 
    \+ stepping_on(agent,carrot,_), 
    position(comestible,carrot,_,_), 
    hostile(steed).

action(getSaddle) :- 
    saddles(X), X == 0, 
    \+ stepping_on(agent,saddle,_), 
    position(applicable,saddle,_,_).

action(pacifySteed) :- 
    hostile(steed), 
    carrots(X), 
    X > 0.

action(hoardCarrots) :- 
    carrots(X), X == 0, 
    \+ hostile(steed), 
    tameness(steed, T), 
    max_tameness(MT), 
    T < MT.

action(feedSteed) :- 
    carrots(X), 
    X > 0, 
    \+ hostile(steed), 
    tameness(steed, T), 
    max_tameness(MT), 
    T < MT.

action(rideSteed) :- 
    rideable(steed), 
    \+ hostile(steed), 
    carrots(X), 
    X == 0, 
    \+ position(comestible,carrot,_,_).

%we need to explore if the pony is tamed but we dont't know where it is
%we need to ecplore if the pony is not tamed and we don't have carrots
%TODO: we can decide to explore if we haven't enough carrots to tame the pony
action(explore) :- 
    (tameness(_, T), max_tameness(MT)),
    ((T == MT, \+ position(_, Steed, _, _), is_steed(Steed)); 
    (T < MT, carrots(X), X == 0, \+ position(_, carrot, _, _))).

%%% INTERRUPT CONDITIONS
interrupt(getCarrot) :- 
    carrots(X), X > 0; 
    stepping_on(agent,carrot,_); 
    \+ position(comestible,carrot,_,_); 
    \+ hostile(steed).

interrupt(getSaddle) :- 
    saddles(X), X > 0; 
    stepping_on(agent,saddle,_); 
    \+ position(applicable,saddle,_,_).
interrupt(pacifySteed) :- 
    \+ hostile(steed); 
    carrots(X), 
    X == 0. % steed distance further than carrot? Need to differentiate between getting the first carrot and the subsequents
interrupt(feedSteed) :- 
    carrots(X), X == 0; 
    (tameness(steed, T), max_tameness(MT), T == MT).
interrupt(rideSteed) :- 
    \+ rideable(steed); 
    hostile(steed); 
    ((carrots(X), X > 0); position(comestible,carrot,_,_), (tameness(steed, T), max_tameness(MT), T < MT)).
interrupt(hoardCarrots) :- (carrots(X), tameness(steed, T), max_tameness(MT), T+X >= MT); hostile(steed).

interrupt(explore) :- \+ action(explore).

% We need to count how many times we fed the steed to calculate its tameness.
increment_action_count(A) :- retract(action_count(A, N)),  % remove the old value. At initialization the we assert action_count(A, 0) for A = feed
                             NewN is N+1, % increment the value
                             assert(action_count(A, NewN)). % assert the new value

increment_tameness(X) :- retract(tameness(X, N)),  % remove the old value. At initialization we assert tameness(X, 1) for X = steed
                         NewN is N+1, % increment the value
                         assert(tameness(X, NewN)). % assert the new value

% Decreased when using the ride action
decrease_tameness(X) :- retract(tameness(X, N)),  % remove the old value.
                         NewN is N-1, % increment the value
                         assert(tameness(X, NewN)). % assert the new value

feed(X) :- increment_action_count(feed), increment_tameness(X).

% We make use of hostile(steed) predicate. But when is a steed hostile?
% Very naively, I'd say that
% we infer it from the screen description. If the steed is peaceful, it says "tame pony/horse/etc"
% hostile(steed) :- tameness(steed, T), T < 2. In the 1% chance the steed spawns peaceful, it will nevertheless start with tameness = 1

% We need to check this if we are to throw carrots at a horse.
is_aligned(R1,C1,R2,C2) :- R1 == R2; C1 == C2; ((R1 is R2+X;R1 is R2-X), (C1 is C2+X;C1 is C2-X)).

% Directionality and space conditions, taken from handson2
% test the different condition for closeness
% two objects are close if they are at 1 cell distance, including diagonals
is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).

% check if the selected direction is safe
safe_direction(R, C, D,Direction) :- resulting_position(R, C, NewR, NewC, D),
                                      ( safe_position(NewR, NewC) ->Direction = D;
                                      % else, get a new close direction
                                      % and check its safety
                                      close_direction(D, ND), safe_direction(R, C, ND,Direction)
                                      ).

% a square is unsafe if there is a trap or an enemy
unsafe_position(R, C) :- position(trap,_, R, C).
unsafe_position(R, C) :- position(enemy,_, R, C).
unsafe_position(R,C) :- 
    position(enemy,_, ER, EC), 
    is_close(ER, EC, R, C).
unsafe_position(_,_) :- fail.
% \+ means "the proposition is not entailed by KB". Sort of a not, but more general
safe_position(R,C) :- \+ unsafe_position(R,C).

%%%% known facts %%%%
opposite(north, south).
opposite(south, north).
opposite(east, west).
opposite(west, east).
opposite(northeast, southwest).
opposite(southwest, northeast).
opposite(northwest, southeast).
opposite(southeast, northwest).

resulting_position(R, C, NewR, NewC, north) :-
    NewR is R-1, NewC = C.
resulting_position(R, C, NewR, NewC, south) :-
    NewR is R+1, NewC = C.
resulting_position(R, C, NewR, NewC, west) :-
    NewR = R, NewC is C-1.
resulting_position(R, C, NewR, NewC, east) :-
    NewR = R, NewC is C+1.
resulting_position(R, C, NewR, NewC, northeast) :-
    NewR is R-1, NewC is C+1.
resulting_position(R, C, NewR, NewC, northwest) :-
    NewR is R-1, NewC is C-1.
resulting_position(R, C, NewR, NewC, southeast) :-
    NewR is R+1, NewC is C+1.
resulting_position(R, C, NewR, NewC, southwest) :-
    NewR is R+1, NewC is C-1.

close_direction(north, northeast).
close_direction(northeast, east).
close_direction(east, southeast).
close_direction(southeast, south).
close_direction(south, southwest).
close_direction(southwest, west).
close_direction(west, northwest).
close_direction(northwest, north).

% we need to pick a carrot if we are stepping on it. 
is_pickable(carrots).

% what is a steed?
is_steed(steed).
is_steed(pony).
is_steed(horse).
is_steed(warhorse).
carrots(0).
saddles(0).
tameness(steed, 1). % tameness is 1 at the beginning of the game
action_count(feed, 0).
max_tameness(20).