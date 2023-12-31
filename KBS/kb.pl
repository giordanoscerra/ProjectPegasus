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
:- dynamic unencumbered/1.
:- dynamic saddled/1.
% semantics: has(ownerCategory,owner,ownedObjectCat,ownedObject)
:- dynamic has/4.   % It could be recycled for the carrots(X) thing

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
rideable(X) :- is_steed(X), saddled(X), \+ riding(agent,_), \+ hallucinating(agent), \+ wounded_legs(agent), \+ encumbered(agent), \+ (blind(agent), \+ telepathic(agent)), \+ punished(agent)
    , \+ trapped(agent), \+ (wearing(agent, Y), (rusty(Y); corroded(Y))). % I do not intend to implement everything but we can do what we can in the time we have, as a flex

% You will always fail and slip if any of the following apply:[3]
% 
%     You are confused.
%     You are fumbling.
%     You have slippery fingers.
%     Your steed's saddle is cursed.
slippery :- confused(agent); fumbling(agent); slippery_fingers(agent). % WHAT IF THE SADDLE IS CURSED??????

unencumbered(agent) :- \+ burdened(agent), \+ stressed(agent), \+ strained(agent), \+ overtaxed(agent), \+ overloaded(agent).
encumbered(agent) :- stressed(agent); strained(agent); overtaxed(agent); overloaded(agent). %no burdened?

%%% GENERAL SUBTASKS feel free to add other conditions or comments to suggest them

action(pick) :-
    stepping_on(agent,ObjClass,Obj),
    is_pickable(ObjClass),
    (
        ( %the bject is a saddle
            (Obj == saddle),
            (
                (max_tameness(MT), tameness(Steed,T), is_steed(Steed), carrots(X), MT - T > X); % can start mounting procedure
                starvationRiding % there is nothing we can do to tame the pony
            )
        );
        ( %the object is not a saddle
            \+ (Obj == saddle)
        )
    ).

action(getCarrot) :- 
    carrots(X), is_steed(Steed), \+ stepping_on(agent,_,carrot), position(comestible,carrot,_,_), 
    (
        (X == 0, hostile(Steed));
        (max_tameness(MT), tameness(Steed,T), MT - T > X, 
        \+ hostile(Steed))
    ).    % Can be stopped if danger (to implement)


action(getSaddle) :- 
    saddles(X), X == 0, \+ stepping_on(agent,_,saddle), position(applicable,saddle,_,_),  
    (
        ( 
            tameness(Steed,MT),
            max_tameness(MT),
            is_steed(Steed)
        );
        (
            starvationRiding
        )
    ).


% The idea is: if the pony isn't in sight the agent can hoard carrots in the meantime
action(feedSteed) :- 
    is_steed(Steed), carrots(X), position(steed,Steed,RS,CS),position(agent,agent,RA,CA),
    (
        (
            hostile(Steed), X > 0  % if the pony is far away, but there are enemies then fight may be worthwile
        );
        (
            \+hostile(Steed), % consider enemies if they are close
            (
                is_close(RA,CA,RS,CS);  %not hostile but close
                (tameness(Steed,T), max_tameness(MT), X >= MT - T) %max tameanes can be reached
            )
        );
        (
            starvationRiding, X > 0
        )
    ).

action(applySaddle) :- 
    saddles(X), X > 0,
    is_steed(Steed),
    \+ saddled(Steed),
    position(steed, Steed, _, _),
    (
        (max_tameness(MT),tameness(Steed,MT));
        (starvationRiding)
    ).

action(rideSteed) :- 
    rideable(Steed), 
    \+ hostile(Steed),
    position(steed, Steed, _, _),
    (
        (max_tameness(MT),tameness(Steed,T), T >= MT);
        (starvationRiding)
    ).


%we need to explore if the pony is/can_be tamed but we dont't know where it is
%we need to explore if the pony is not tamed and we don't have carrots
action(explore) :- 
    (tameness(Steed, T), max_tameness(MT), carrots(X), is_steed(Steed)),
    (
        (X >= MT - T, \+ position(_, Steed, _, _)); 
        (X < MT - T, \+ position(comestible, carrot, _, _))
    ).

%%% INTERRUPT CONDITIONS
%TODO: add conditions for enemies

% if you can't prove that this is wrong please don't change it
interrupt(getCarrot) :- \+ stepping_on(agent, comestible, carrot), \+ action(getCarrot).

interrupt(getSaddle) :- \+ stepping_on(agent, applicable, saddle), \+ action(getSaddle).

interrupt(feedSteed) :- 
    (carrots(X), X == 0); 
    (tameness(Steed, T), is_steed(Steed), max_tameness(MT), T == MT);
    (\+ position(_, Steed, _, _)).

interrupt(applySaddle) :- \+ action(applySaddle).

interrupt(rideSteed) :- \+ action(rideSteed).

interrupt(explore) :- \+ action(explore).

% We make use of hostile(steed) predicate. But when is a steed hostile?
% Very naively, I'd say that
% we infer it from the screen description. If the steed is peaceful, it says "tame/peaceful pony/horse/etc"
% hostile(Steed) :- is_steed(Steed), tameness(Steed, T), T < 2. In the 1% chance the steed spawns peaceful, it will nevertheless start with tameness = 1

% Directionality and space conditions, taken from handson2
% test the different condition for closeness
% two objects are close if they are at 1 cell distance, including diagonals
is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).


%%%% KNOWN FACTS %%%%

% we need to pick a carrot if we are stepping on it. 
is_pickable(comestible).
is_pickable(applicable).
is_pickable(weapon).

% what is a steed? it's a horse-like creature. "destriero" in italian.
is_steed(steed).
is_steed(pony).
is_steed(horse).
is_steed(warhorse).
max_tameness(20).

%%% INITIALIZATION %%%

% if we have explored the map 3 times and the pony is not tamed
% we should accept the fact that we cannot tame it (maybe he stole some carrots)
% so we should try to ride it anyway
fullyExplored(0).
starvationRiding :- fullyExplored(X), X > 2, \+ position(comestible, carrot, _, _), carrots(0).

% if pony dies ???

carrots(0).
saddles(0).
% tameness is 1 at the beginning of the game
%tameness(steed, 1).
tameness(pony, 1).
tameness(horse, 1).
tameness(warhorse, 1).

%add wait conditions if agent has saddle and steed is tamed
%also enemies close to the pony (save the pony Ryan)