# ML Flow
The hidden assumption: 
"I will remember how this model was created"

###### What's an ML Experiment
code
data
parameteres
randomness
environment

###### What git captures(and what it doesn't)
code changes - yes
parameters - No
metrics - No
artifacts - No
environment - No
The core problem: ML systems lose decision history

###### Why this becomes dangerous in production
Model retraining
data drift
team changes
Infrastructure changes

###### The question every production team msut answer
"Why is this model in production"

###### What happens without tracking
No reproducibility
no auditability
no safe rollbacks
no trust

###### Common Early-Stage Excuses
We'll clean it up later
this is just research
Tracking slows us down

###### Wha tbreaks first at scale
Folder based Tracking
Spreadsheet comparisions
Memory-based decisions

###### This is not. atooling problem
This is a system and discipline problem