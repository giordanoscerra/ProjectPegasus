:- dynamic position/4.
:- dynamic wields_weapon/2.
:- dynamic health/1.
:- dynamic has/3.
:- dynamic stepping_on/3.
:- dynamic unsafe_position/2.

% TODO: RULES FOR ACTION SELECTION
%REMEMBER: The action rules are ordered by priority
% For movement actions, always check is the direction selected is safe.

% eat the apple and win the game
% Requirements:
%   + agent must have a comestible apple
action(eat) :- has(agent,comestible,_).

% attack an enemy
% the attack is automatic when you move towards it
% in this case, it is useless to check if the new position is safe - it is already occupied by the enemy
% Requirements:
%   + agent must be at a certain position
%   + enemy must be at a certain position
%   + agent is weilding a weapon
%   + enemy is beatable with the weapon
%   + agent and enemy are close
%   + agent is healthy
%   + next step is in the direction towards the enemy
action(attack(Direction)) :- 
    position(agent,_,RA,CA), 
    position(enemy,Enemy,RE,CE), 
    wields_weapon(agent,Weapon),  
    is_beatable(Enemy,Weapon), 
    is_close(RA,CA,RE,CE), 
    healthy, 
    next_step(RA,CA,RE,CE,Direction).

% run away from an enemy, when it is not safe to attack
% choose the opposite direction wrt the enemy position
% Requirements:
%   + agent must be at a certain position
%   + enemy must be at a certain position
%   + agent and enemy are close
%   + agent is not healthy
%   + next step is in the direction towards the enemy
%   + define the opposite direction wrt the next step one
%   + the opposite direction is a safe direction
action(run(OppositeDirection)) :- 
    position(agent,_,RA,CA),
    position(enemy,_,RE,CE),
    is_close(RA,CA,RE,CE),
    not(healthy),
    next_step(RA,CA,RE,CE,D),
    opposite(OD,D),
    safe_direction(RA,CA,OD,OppositeDirection).

% if not wielded, go towards the weapon available in the map
% Requirements:
%   + agent must be at a certain position
%   + enemy must be at a certain position
%   + agent and enemy are close
%   + agent is weilding a weapon
%   + enemy is not beatable with the weapon
%   + the weapon is at a given position
%   + next step is in the direction towards the weapon
%   + the next step direction is safe
action(get_to_weapon(Direction)) :- 
    position(agent,_,RA,CA),
    position(enemy,Enemy,RE,CE),
    is_close(RA,CA,RE,CE),
    wields_weapon(agent,Weapon),
    \+ is_beatable(Enemy,Weapon),
    position(weapon,_,RW,CW),
    next_step(RA,CA,RW,CW,D),
    safe_direction(RA,CA,D,Direction).

% pick up an object
% Requirements:
%   + agent is stepping on a generic object (hint: you can use 'ObjClass' and ignore the name of the object)
%   + the class of object is pickable
action(pick) :- 
    stepping_on(agent,ObjClass,_),
    is_pickable(ObjClass). 

% if the agent has a weapon, wield it
% Requirements:
%   + agent has a weapon with a given name ('Weapon')
action(wield(Weapon)) :- has(agent,weapon,Weapon).

% If you cannot apply previous rules, just go towards the goal
% get the next movement to get closer to the goal
% Requirements:
%   + agent must be at a certain position
%   + the comestible apple must be at a certain position
%   + next step is towards the apple
%   + next step direction is a safe direction
action(move(Direction)) :- 
    position(agent,_,RA,CA),
    position(comestible,_,Robj,Cobj),
    next_step(RA,CA,Robj,Cobj,D),
    safe_direction(RA,CA,D,Direction).

% If the apple is not visible on the map - e.g. the enemy took it
% Try to kill it, if beatable
% Requirements:
%   + apple is not found at any position
%   + agent must be at a certain position
%   + enemy must be at a certain position
%   + agent is wielding a weapon
%   + enemy is beatable with the weapon
%   + next step is towards the enemy
%   + next step direction is a safe direction
action(move_towards_enemy(Direction)) :- 
    not(position(comestible,apple,_,_)),
    position(agent,_,RA,CA),
    position(enemy,Enemy,RE,CE),
    wields_weapon(agent,Weapon),
    is_beatable(Enemy,Weapon),
    next_step(RA,CA,RE,CE,D),
    safe_direction(RA,CA,D,Direction).


% If not beatable, go towards the weapon
% Requirements:
%   + apple is not found at any position
%   + agent must be at a certain position
%   + enemy must be at any position
%   + agent is wielding a weapon
%   + enemy is not beatable with the weapon
%   + weapon must be at a certain position
%   + next step is towards the weapon
%   + next step direction is a safe direction
action(get_to_weapon(Direction)) :- 
    not(position(comestible,apple,_,_)),
    position(agent,_,RA,CA),
    position(enemy,Enemy,_,_),
    wields_weapon(agent,WieldedWeapon),
    not(is_beatable(Enemy,WieldedWeapon)),
    position(weapon,_,RW,CW),
    next_step(RA,CA,RW,CW,D),
    safe_direction(RA,CA,D,Direction).


% -----------------------------------------------------------------------------------------------

% test the different condition for closeness
% two objects are close if they are at 1 cell distance, including diagonals
is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).

% the agent can perform "dangerous" actions - e.g. attack a monster - if its health is above 50%
healthy :- health(H), H > 50.

% compute the direction given the starting point and the target position
% check if the direction leads to a safe position
% D = temporary direction - may be unsafe
%Direction = the definitive direction 
next_step(R1,C1,R2,C2, D) :-
    ( R1 == R2 -> ( C1 > C2 -> D = west; D = east );
    ( C1 == C2 -> ( R1 > R2 -> D = north; D = south);
    ( R1 > R2 ->
        ( C1 > C2 -> D = northwest; D = northeast );
        ( C1 > C2 -> D = southwest; D = southeast )
    ))).
    % safe_direction(R1, C1, D,Direction).

% check if the selected direction is safe
safe_direction(R, C, D,Direction) :- resulting_position(R, C, NewR, NewC, D),
                                      ( safe_position(NewR, NewC) ->Direction = D;
                                      % else, get a new close direction
                                      % and check its safety
                                      close_direction(D, ND), safe_direction(R, C, ND,Direction)
                                      ).

% a square if unsafe if there is a trap or an enemy
unsafe_position(R, C) :- position(trap,_, R, C).
unsafe_position(R, C) :- position(enemy,_, R, C).
unsafe_position(R,C) :- 
    position(enemy,_, ER, EC), 
    is_close(ER, EC, R, C).



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

has(agent,_,_) :- fail.

unsafe_position(_,_) :- fail.
% \+ means "the proposition is not entailed by KB". Sort of a not, but more general
safe_position(R,C) :- \+ unsafe_position(R,C).

is_beatable(kobold,_).
is_beatable(giantmummy, tsurugi).

is_pickable(comestible).
is_pickable(weapon).