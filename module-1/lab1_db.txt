%swords
sword(wooden_sword).
sword(stone_sword).
sword(iron_sword).
sword(gold_sword).
sword(diamond_sword).

%pickaxes
pickaxe(wooden_pickaxe).
pickaxe(stone_pickaxe).
pickaxe(iron_pickaxe).
pickaxe(gold_pickaxe).
pickaxe(diamond_pickaxe).

%blocks
block(planks).
block(dirt).
block(grass).
block(cobblestone).
block(workbench).
block(furnance).
block(wood).
block(stone).
block(coal_ore).
block(iron_ore).
block(gold_ore).
block(diamond_ore).
block(bedrock).

%resources
resource(stick).
resource(string).
resource(seed).
resource(wheet).
resource(coal).
resource(iron).
resource(gold).
resource(diamond).

%Items
item(X) :- sword(X).
item(X) :- pickaxe(X).
item(X) :- block(X).
item(X) :- resource(X).

%workbench recipes
recipe([wood], [planks, planks, planks, planks]).
recipe([planks, planks], [stick, stick, stick, stick]).
recipe([stick, planks, planks], [wooden_sword]).
recipe([stick, cobblestone, cobblestone], [stone_sword]).
recipe([stick, iron, iron], [iron_sword]).
recipe([stick, gold, gold], [gold_sword]).
recipe([stick, diamond, diamond], [diamond_sword]).
recipe([stick, stick, planks, planks, planks], [wooden_pickaxe]).
recipe([stick, stick, cobblestone, cobblestone, cobblestone], [stone_pickaxe]).
recipe([stick, stick, iron, iron, iron], [iron_pickaxe]).
recipe([stick, stick, gold, gold, gold], [gold_pickaxe]).
recipe([stick, stick, diamond, diamond, diamond], [diamond_pickaxe]).
recipe([stick, stick, planks, planks, planks], [wooden_axe]).
recipe([stick, stick, cobblestone, cobblestone, cobblestone], [stone_axe]).
recipe([stick, stick, iron, iron, iron], [iron_axe]).
recipe([stick, stick, gold, gold, gold], [gold_axe]).
recipe([stick, stick, diamond, diamond, diamond], [diamond_axe]).
recipe([planks, planks, planks, planks], [workbench]).
recipe([cobblestone, cobblestone, cobblestone, cobblestone, cobblestone, cobblestone, cobblestone, cobblestone], [furnance]).

%furnance recipes
furnance_recipe([cobblestone], [stone]).
furnance_recipe([iron_ore], [iron]).
furnance_recipe([gold_ore], [gold]).

%remove requirements from inventory
use_for_craft(Inv, [], Inv2) :- Inv2 = Inv.
use_for_craft(Inv, [Req_H | Req_T], Inv2) :- excl(Req_H, Inv, InvT), use_for_craft(InvT, Req_T, Inv2).

%add crafted items to inventory
get_crafted(Inv, [], Inv2) :- Inv2 = Inv.
get_crafted(Inv, [Req_H | Req_T], Inv2) :- incl(Req_H, Inv, InvT), get_crafted(InvT, Req_T, Inv2).	

%get items which we can melt down
available_furnance_craft(Inv, Items) :- furnance_recipe(X, Items), list_contains(Inv, X).

%check can we melt down Item using our inventory
can_melted(Inv, Item) :- furnance_recipe(X, Items), member(Item, Items), list_contains(Inv, X), write(Item), write(" can be melted down"); write(Item), write(" can't be melted down"), false.

%melt down some materials to get X
meltdown(Inv, X, Inv2) :- can_melted(Inv, X), furnance_recipe(Y, Z), member(X, Z), (member(coal, Inv); write("there is no coal in inventory"), false), !, use_for_craft(Inv, Y, Inv_T), use_for_craft(Inv_T, [coal], Inv_TT), get_crafted(Inv_TT, Z, Inv2).

%get items which we can craft
available_crafts(Inv, Items) :- recipe(X, Items), list_contains(Inv, X). 
can_craft(Inv, Item) :- recipe(X, Items), member(Item, Items), list_contains(Inv, X), write(Item), write(" can be crafted"); write(Item), write("can't be crafted "), false.
    
%craft some items to get X
craft(Inv, X, Inv2) :- can_craft(Inv, X), recipe(Y, Z), member(X, Z), !, use_for_craft(Inv, Y, Inv_T), get_crafted(Inv_T, Z, Inv2), write(Z), write(" was crafted").

%simple interaction with inventory
get_item(X, Inv, Inv2) :- item(X), incl(X, Inv, Inv2).
remove_item(X, Inv, Inv2) :- excl(X, Inv, Inv2).

%rules for lists
incl(H, T, [H | T]). 
excl( _, [], []).
excl( R, [R|T], T).
excl( R, [H|T], [H|T2]) :- H \= R, excl( R, T, T2).
list_contains(_, []) :- !.
list_contains(L1, [L2_H | L2_T]) :- member(L2_H, L1), !, excl(L2_H, L1, LL1), list_contains(LL1, L2_T). 
