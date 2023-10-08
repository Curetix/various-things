# Regex Patterns for finding Classes / Skills
Class obtained: `\[(?<class_name>.+)\sClass\sObtained!\]` captures *class_name*

Class levelup: `\[(?<class_name>.+)\sLevel\s(?<level>\d{1,2})!\]` captures *class_name*, *level*

Class changed: `\[Conditions\s[Mm]et:\s(?<old_class>.+)\s→\s(?<new_class>.+)\sClass!\]` captures *old_class*, *new_class*

Class consolidated: `\[Class\sConsolidation:\s(?P<removed_class>.+)\sremoved.\]` captures *removed_class*

Skill obtained: `\[Skill\s–\s(?<skill_name>.+)\s[Oo]btained!\]` captures *skill_name*

Skill learned: `\[Skill\s–\s(?<skill_name>.+)\s[Ll]earned.\]` captures *skill_name*

Skill changed: `\[Skill\sChange\s–\s(?<old_skill>.+)\s→\s(?<new_skill>.+)!\]` captures *old_skill*, *new_skill*

# Erin

## 1.01
[Innkeeper Class Obtained!]  
[Innkeeper Level 1!]  
[Skill – Basic Cleaning obtained!]  
[Skill – Basic Cooking obtained!]

## 1.03
[Innkeeper Level 4!]

## 1.07
[Innkeeper Level 5!]  
[Skill – Basic Crafting obtained!]

## 1.14
[Innkeeper Level 6!]

## 1.16
[Innkeeper Level 9!]  
[Skill – Tavern Brawling obtained!]  
[Skill – Unerring Throw obtained!]

## 1.22
[Innkeeper Level 10!]  
[Skill – Alcohol Brewer obtained!]  
[Skill – Dangersense obtained!]

## 1.28
[Innkeeper Level 11!]  
[Skill – Lesser Strength Obtained!]  
**[Skill – Immortal Moment Learned.]**

## 1.33
[Innkeeper Level 13!]  
[Skill – Loud Voice obtained!]

## 1.38
[Innkeeper Level 15!]

## 1.41
[Skill – Power Strike Learned.]

## 1.45 
[Innkeeper Level 18!]  
[Skill – Immunity: Alcohol obtained!]  
[Skill – Quick Recovery obtained!]

## 2.07
[Warrior Class Obtained!]  
[Warrior Level 2!]  
[Skill – Lesser Endurance Obtained!]

## 2.11
[Innkeeper Level 19!]

## 2.17
[Innkeeper Level 21!]  
[Skill – Advanced Cooking Obtained!]  
[Skill – Advanced Crafting Obtained!]  
[Singer Class Obtained!]  
[Singer Level 6!]  
[Skill – Perfect Recall Obtained!]  
[Skill – Control Pitch Obtained!]  

## 2.21
[Innkeeper Level 25!]  
[Skill – Inn’s Aura Obtained!]  
**[Skill – Wondrous Fare Learned.]**  

## 2.43
[Innkeeper Level 26!]