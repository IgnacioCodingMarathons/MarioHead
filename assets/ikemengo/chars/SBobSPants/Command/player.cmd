; The CMD file.
;
; Two parts: 1. Command definition and  2. State entry
; (state entry is after the commands def section)
;
; 1. Command definition
; ---------------------
; Note: The commands are CASE-SENSITIVE, and so are the command names.
; The eight directions are:
;   B, DB, D, DF, F, UF, U, UB     (all CAPS)
;   corresponding to back, down-back, down, downforward, etc.
; The six buttons are:
;   a, b, c, x, y, z               (all lower case)
;   In default key config, abc are are the bottom, and xyz are on the
;   top row. For 2 button characters, we recommend you use a and b.
;   For 6 button characters, use abc for kicks and xyz for punches.
;
; Each [Command] section defines a command that you can use for
; state entry, as well as in the CNS file.
; The command section should look like:
;
;   [Command]
;   name = some_name
;   command = the_command
;   time = time (optional -- defaults to 15 if omitted)
;
; - some_name
;   A name to give that command. You'll use this name to refer to
;   that command in the state entry, as well as the CNS. It is case-
;   sensitive (QCB_a is NOT the same as Qcb_a or QCB_A).
;
; - command
;   list of buttons or directions, separated by commas.
;   Directions and buttons can be preceded by special characters:
;   slash (/) - means the key must be held down
;          egs. command = /D       ;hold the down direction
;               command = /DB, a   ;hold down-back while you press a
;   tilde (~) - to detect key releases
;          egs. command = ~a       ;release the a button
;               command = ~D, F, a ;release down, press fwd, then a
;          If you want to detect "charge moves", you can specify
;          the time the key must be held down for (in game-ticks)
;          egs. command = ~30a     ;hold a for at least 30 ticks, then release
;   dollar ($) - Direction-only: detect as 4-way
;          egs. command = $D       ;will detect if D, DB or DF is held
;               command = $B       ;will detect if B, DB or UB is held
;   plus (+) - Buttons only: simultaneous press
;          egs. command = a+b      ;press a and b at the same time
;               command = x+y+z    ;press x, y and z at the same time
;   You can combine them:
;     eg. command = ~30$D, a+b     ;hold D, DB or DF for 30 ticks, release,
;                                  ;then press a and b together
;   It's recommended that for most "motion" commads, eg. quarter-circle-fwd,
;   you start off with a "release direction". This matches the way most
;   popular fighting games implement their command detection.
;
; - time (optional)
;   Time allowed to do the command, given in game-ticks. Defaults to 15
;   if omitted
;
; If you have two or more commands with the same name, all of them will
; work. You can use it to allow multiple motions for the same move.
;
; Some common commands examples are given below.
;
; [Command] ;Quarter circle forward + x
; name = "QCF_x"
; command = ~D, DF, F, x
;
; [Command] ;Half circle back + a
; name = "HCB_a"
; command = ~F, DF, D, DB, B, a
;
; [Command] ;Two quarter circles forward + y
; name = "2QCF_y"
; command = ~D, DF, F, D, DF, F, y
;
; [Command] ;Tap b rapidly
; name = "5b"
; command = b, b, b, b, b
; time = 30
;
; [Command] ;Charge back, then forward + z
; name = "charge_B_F_z"
; command = ~60$B, F, z
; time = 10
; 
; [Command] ;Charge down, then up + c
; name = "charge_D_U_c"
; command = ~60$D, U, c
; time = 10
; 

;-| Button Remapping |-----------------------------------------------------
; This section lets you remap the player's buttons (to easily change the
; button configuration). The format is:
;   old_button = new_button
; If new_button is left blank, the button cannot be pressed.
[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s

;-| Default Values |-------------------------------------------------------
[Defaults]
; Default value for the "time" parameter of a Command. Minimum 1.
command.time = 30

; Default value for the "buffer.time" parameter of a Command. Minimum 1,
; maximum 30.
command.buffer.time = 1

;-| AI |----------------------------------------------------
[Command]
name = "AI_1"
command = D, D, D, D, D, D, D, D, D, D, D, D, D, D, D
time = 1

[Command]
name = "AI_2"
command = F, F, F, F, F, F, F, F, F, F, F, F, F, F, F
time = 1

[Command]
name = "AI_3"
command = U, U, U, U, U, U, U, U, U, U, U, U, U, U, U
time = 1

[Command]
name = "AI_4"
command = B, B, B, B, B, B, B, B, B, B, B, B, B, B, B
time = 1

[Command]
name = "AI_5"
command = a, a, a, a, a, a, a, a, a, a, a, a, a, a, a
time = 1

[Command]
name = "AI_6"
command = b, b, b, b, b, b, b, b, b, b, b, b, b, b, b
time = 1

[Command]
name = "AI_7"
command = c, c, c, c, c, c, c, c, c, c, c, c, c, c, c
time = 1

[Command]
name = "AI_8"
command = x, x, x, x, x, x, x, x, x, x, x, x, x, x, x
time = 1

[Command]
name = "AI_9"
command = y, y, y, y, y, y, y, y, y, y, y, y, y, y, y
time = 1

[Command]
name = "AI_10"
command = z, z, z, z, z, z, z, z, z, z, z, z, z, z, z
time = 1

[Command]
name = "AI_11"
command = s, s, s, s, s, s, s, s, s, s, s, s, s, s, s
time = 1

[Command]
name = "AI_12"
command = F, F, F, F, F, F, F, F, F, F, F, F, F, F, a
time = 1

[Command]
name = "AI_13"
command = U, U, U, U, U, U, U, U, U, U, U, U, U, U, a
time = 1

[Command]
name = "AI_14"
command = B, B, B, B, B, B, B, B, B, B, B, B, B, B, a
time = 1

[Command]
name = "AI_15"
command = a, a, a, a, a, a, a, a, a, a, a, a, a, a, b
time = 1

[Command]
name = "AI_16"
command = b, b, b, b, b, b, b, b, b, b, b, b, b, b, a
time = 1

[Command]
name = "AI_17"
command = c, c, c, c, c, c, c, c, c, c, c, c, c, c, a
time = 1

[Command]
name = "AI_18"
command = x, x, x, x, x, x, x, x, x, x, x, x, x, x, a
time = 1

[Command]
name = "AI_19"
command = y, y, y, y, y, y, y, y, y, y, y, y, y, y, a
time = 1

[Command]
name = "AI_20"
command = z, z, z, z, z, z, z, z, z, z, z, z, z, z, a
time = 1

[Command]
name = "AI_21"
command = s, s, s, s, s, s, s, s, s, s, s, s, s, s, a
time = 1

[Command]
name = "AI_22"
command = F, F, F, F, F, F, F, F, F, F, F, F, F, F, b
time = 1

[Command]
name = "AI_23"
command = U, U, U, U, U, U, U, U, U, U, U, U, U, U, b
time = 1

[Command]
name = "AI_24"
command = B, B, B, B, B, B, B, B, B, B, B, B, B, B, b
time = 1

[Command]
name = "AI_25"
command = a, a, a, a, a, a, a, a, a, a, a, a, a, a, c
time = 1

[Command]
name = "AI_26"
command = b, b, b, b, b, b, b, b, b, b, b, b, b, b, c
time = 1

[Command]
name = "AI_27"
command = c, c, c, c, c, c, c, c, c, c, c, c, c, c, b
time = 1

[Command]
name = "AI_28"
command = x, x, x, x, x, x, x, x, x, x, x, x, x, x, b
time = 1

[Command]
name = "AI_29"
command = y, y, y, y, y, y, y, y, y, y, y, y, y, y, b
time = 1

[Command]
name = "AI_30"
command = z, z, z, z, z, z, z, z, z, z, z, z, z, z, b
time = 1

[Command]
name = "AI_31"
command = s, s, s, s, s, s, s, s, s, s, s, s, s, s, b
time = 1

[Command]
name = "AI_32"
command = F, F, F, F, F, F, F, F, F, F, F, F, F, F, c
time = 1

[Command]
name = "AI_33"
command = U, U, U, U, U, U, U, U, U, U, U, U, U, U, c
time = 1

[Command]
name = "AI_34"
command = B, B, B, B, B, B, B, B, B, B, B, B, B, B, c
time = 1

[Command]
name = "AI_35"
command = a, a, a, a, a, a, a, a, a, a, a, a, a, a, x
time = 1

[Command]
name = "AI_36"
command = b, b, b, b, b, b, b, b, b, b, b, b, b, b, x
time = 1

[Command]
name = "AI_37"
command = c, c, c, c, c, c, c, c, c, c, c, c, c, c, x
time = 1

[Command]
name = "AI_38"
command = x, x, x, x, x, x, x, x, x, x, x, x, x, x, c
time = 1

[Command]
name = "AI_39"
command = y, y, y, y, y, y, y, y, y, y, y, y, y, y, c
time = 1

[Command]
name = "AI_40"
command = z, z, z, z, z, z, z, z, z, z, z, z, z, z, c
time = 1

;-| Super Motions |--------------------------------------------------------

[Command]
name = "Hyper1" 
command = x+y
time = 10

[Command]
name = "Hyper2" 
command = a+b
time = 10

;-| Special Motions |------------------------------------------------------
[Command]
Name = "Special1"
command = ~D, DF, F, x
Time = 10

[Command]
Name = "Special1"
command = ~D, DF, F, y
Time = 10

[Command]
Name = "Special1"
command = ~D, DF, F, z
Time = 10

[Command]
Name = "SSpecial1"
command = ~D, DB, B, x
Time = 10

[Command]
Name = "SSpecial1"
command = ~D, DB, B, y
Time = 10

[Command]
Name = "SSpecial1"
command = ~D, DB, B, z
Time = 10

[Command]
Name = "Special2"
command = ~D, DF, F, a
Time = 10

[Command]
Name = "Special2"
command = ~D, DF, F, b
Time = 10

[Command]
Name = "Special2"
command = ~D, DF, F, c
Time = 10

[Command]
Name = "SSpecial2"
command = ~D, DB, B, a
Time = 10

[Command]
Name = "SSpecial2"
command = ~D, DB, B, b
Time = 10

[Command]
Name = "SSpecial2"
command = ~D, DB, B, c
Time = 10

;-------------------------------------------------------------------------------
;Helpers
[Command]
Name = "Helper1"
command = a+x
Time = 10

[Command]
Name = "Helper2"
command = b+y
Time = 10

[Command]
Name = "Helper3"
command = c+z
Time = 10

;-| Double Tap |-----------------------------------------------------------
[Command]
name = "FF"     ;Required (do not remove)
command = F, F
time = 10

[Command]
name = "BB"     ;Required (do not remove)
command = B, B
time = 10

;-| 2/3 Button Combination |-----------------------------------------------
[Command]
name = "recovery" ;Required (do not remove)
command = x+y
time = 1

[Command]
name = "recovery"
command = y+z
time = 1

[Command]
name = "recovery"
command = x+z
time = 1

[Command]
name = "recovery"
command = a+b
time = 1

[Command]
name = "recovery"
command = b+c
time = 1

[Command]
name = "recovery"
command = a+c
time = 1

;-| Dir + Button |---------------------------------------------------------
[Command]
name = "back_x"
command = /$B,x
time = 1

[Command]
name = "back_y"
command = /$B,y
time = 1

[Command]
name = "back_z"
command = /$B,z
time = 1

[Command]
name = "down_x"
command = /$D,x
time = 1

[Command]
name = "down_y"
command = /$D,y
time = 1

[Command]
name = "down_z"
command = /$D,z
time = 1

[Command]
name = "fwd_x"
command = /$F,x
time = 1

[Command]
name = "fwd_y"
command = /$F,y
time = 1

[Command]
name = "fwd_z"
command = /$F,z
time = 1

[Command]
name = "up_x"
command = /$U,x
time = 1

[Command]
name = "up_y"
command = /$U,y
time = 1

[Command]
name = "up_z"
command = /$U,z
time = 1

[Command]
name = "back_a"
command = /$B,a
time = 1

[Command]
name = "back_b"
command = /$B,b
time = 1

[Command]
name = "back_c"
command = /$B,c
time = 1

[Command]
name = "down_a"
command = /$D,a
time = 1

[Command]
name = "down_b"
command = /$D,b
time = 1

[Command]
name = "down_c"
command = /$D,c
time = 1

[Command]
name = "fwd_a"
command = /$F,a
time = 1

[Command]
name = "fwd_b"
command = /$F,b
time = 1

[Command]
name = "fwd_c"
command = /$F,c
time = 1

[Command]
name = "up_a"
command = /$U,a
time = 1

[Command]
name = "up_b"
command = /$U,b
time = 1

[Command]
name = "up_c"
command = /$U,c
time = 1

;-| Single Button |---------------------------------------------------------
[Command]
name = "a"
command = a
time = 1

[Command]
name = "b"
command = b
time = 1

[Command]
name = "c"
command = c
time = 1

[Command]
name = "x"
command = x
time = 1

[Command]
name = "y"
command = y
time = 1

[Command]
name = "z"
command = z
time = 1

[Command]
name = "s"
command = s
time = 1

;-| Single Dir |------------------------------------------------------------
[Command]
name = "fwd" ;Required (do not remove)
command = $F
time = 1

[Command]
name = "downfwd"
command = $DF
time = 1

[Command]
name = "down" ;Required (do not remove)
command = $D
time = 1

[Command]
name = "downback"
command = $DB
time = 1

[Command]
name = "back" ;Required (do not remove)
command = $B
time = 1

[Command]
name = "upback"
command = $UB
time = 1

[Command]
name = "up" ;Required (do not remove)
command = $U
time = 1

[Command]
name = "upfwd"
command = $UF
time = 1

;-| Hold Button |--------------------------------------------------------------
[Command]
name = "hold_x"
command = /x
time = 1

[Command]
name = "hold_y"
command = /y
time = 1

[Command]
name = "hold_z"
command = /z
time = 1

[Command]
name = "hold_a"
command = /a
time = 1

[Command]
name = "hold_b"
command = /b
time = 1

[Command]
name = "hold_c"
command = /c
time = 1

[Command]
name = "hold_s"
command = /s
time = 1

;-| Hold Dir |--------------------------------------------------------------
[Command]
name = "holdfwd" ;Required (do not remove)
command = /$F
time = 1

[Command]
name = "holddownfwd"
command = /$DF
time = 1

[Command]
name = "holddown" ;Required (do not remove)
command = /$D
time = 1

[Command]
name = "holddownback"
command = /$DB
time = 1

[Command]
name = "holdback" ;Required (do not remove)
command = /$B
time = 1

[Command]
name = "holdupback"
command = /$UB
time = 1

[Command]
name = "holdup" ;Required (do not remove)
command = /$U
time = 1

[Command]
name = "holdupfwd"
command = /$UF
time = 1

[Command]
name = "super_jump_up"
command = ~D, U
time = 50

;---------------------------------------------------------------------------
; 2. State entry
; --------------
; This is where you define what commands bring you to what states.
;
; Each state entry block looks like:
;   [State -1, Label]           ;Change Label to any name you want to use to
;                               ;identify the state with.
;   type = ChangeState          ;Don't change this
;   value = new_state_number
;   trigger1 = command = command_name
;   . . .  (any additional triggers)
;
; - new_state_number is the number of the state to change to
; - command_name is the name of the command (from the section above)
; - Useful triggers to know:
;   - statetype
;       S, C or A : current state-type of player (stand, crouch, air)
;   - ctrl
;       0 or 1 : 1 if player has control. Unless "interrupting" another
;                move, you'll want ctrl = 1
;   - stateno
;       number of state player is in - useful for "move interrupts"
;   - movecontact
;       0 or 1 : 1 if player's last attack touched the opponent
;                useful for "move interrupts"
;
; Note: The order of state entry is important.
;   State entry with a certain command must come before another state
;   entry with a command that is the subset of the first.  
;   For example, command "fwd_a" must be listed before "a", and
;   "fwd_ab" should come before both of the others.
;
; For reference on triggers, see CNS documentation.
;
; Just for your information (skip if you're not interested):
; This part is an extension of the CNS. "State -1" is a special state
; that is executed once every game-tick, regardless of what other state
; you are in.


; Don't remove the following line. It's required by the CMD standard.
[Statedef -1]

;===========================================================================
;---------------------------------------------------------------------------
;AI Activation
[State -1, AI Deactivation]
type = VarSet
trigger1 = roundstate = 1
trigger2 = roundstate = 3
trigger3 = roundstate = 4
v = 59
value = 0

;-|-AI-|--------------------------------------------------------------------
[State -1, AI]
type = VarSet
triggerall = roundstate = 2
trigger1 = command = "AI_1"
trigger2 = command = "AI_2"
trigger3 = command = "AI_3"
trigger4 = command = "AI_4"
trigger5 = command = "AI_5"
trigger6 = command = "AI_6"
trigger7 = command = "AI_7"
trigger8 = command = "AI_8"
trigger9 = command = "AI_9"
trigger10 = command = "AI_10"
trigger11 = command = "AI_11"
trigger12 = command = "AI_12"
trigger13 = command = "AI_13"
trigger14 = command = "AI_14"
trigger15 = command = "AI_15"
trigger16 = command = "AI_16"
trigger17 = command = "AI_17"
trigger18 = command = "AI_18"
trigger19 = command = "AI_19"
trigger20 = command = "AI_20"
trigger21 = command = "AI_21"
trigger22 = command = "AI_22"
trigger23 = command = "AI_23"
trigger24 = command = "AI_24"
trigger25 = command = "AI_25"
trigger26 = command = "AI_26"
trigger27 = command = "AI_27"
trigger28 = command = "AI_28"
trigger29 = command = "AI_29"
trigger30 = command = "AI_30"
trigger31 = command = "AI_31"
trigger32 = command = "AI_32"
trigger33 = command = "AI_33"
trigger34 = command = "AI_34"
trigger35 = command = "AI_35"
trigger36 = command = "AI_36"
trigger37 = command = "AI_37"
trigger38 = command = "AI_38"
trigger39 = command = "AI_39"
trigger40 = command = "AI_40"
v = 59
value = 1

;--|-AI Defense-|-----------------------------------------------------------
[State -1]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (p2movetype = A) && (statetype = S)
trigger1 = (p2bodydist X <= 250) && (random <= 979)
value = 130

[State -1]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (p2movetype = A) && (statetype = C)
trigger1 = (p2bodydist X <= 250) && (random <= 979)
value = 131

[State -1]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (p2movetype = A) && (statetype = A)
trigger1 = (p2bodydist X <= 250) && (random <= 979)
value = 132

;-|-AI Combo Attempt-|----------------------------------------------
[State -1,AI Stand Light Punch]
type = ChangeState
value = 200
trigger1 = RoundState = 2 && Var(59) != 0
trigger1 = Ctrl && StateType = S
trigger1 = Random <= 100
trigger1 = (P2BodyDist X = [0,100])

;---------------------------------------------------------------------------
[State -1,AI Stand Light Punch]
type = ChangeState
value = 210
trigger1 = RoundState = 2 && Var(59) != 0
triggerall = P2stateno != [5100,5119]
triggerall = (StateType != A) && (MoveType != H)
triggerall = (P2StateType != A) && (P2life != 0)
trigger1 = P2BodyDist X <= 9
trigger1 = ctrl

;---------------------------------------------------------------------------
[State -1,AI Stand Light Punch]
type = ChangeState
value = 220
trigger1 = RoundState = 2 && Var(59) != 0
trigger1 = Ctrl && StateType = S
trigger1 = Random <= 100
trigger1 = (P2BodyDist X = [0,100])
;---------------------------------------------------------------------------
[State -1,AI Stand Medium Punch]
type = ChangeState
value = 600
trigger1 = RoundState = 2 && Var(59) != 0
trigger1 = Ctrl && StateType = A
trigger1 = Random <= 100
trigger1 = (P2BodyDist X = [0,100])
;---------------------------------------------------------------------------
[State -1,AI Stand Medium Punch]
type = ChangeState
value = 610
trigger1 = RoundState = 2 && Var(59) != 0
trigger1 = Ctrl && StateType = A
trigger1 = Random <= 100
trigger1 = (P2BodyDist X = [0,100])
;---------------------------------------------------------------------------
[State -1,AI Stand Medium Punch]
type = ChangeState
value = 620
trigger1 = RoundState = 2 && Var(59) != 0
trigger1 = Ctrl && StateType = A
trigger1 = Random <= 100
trigger1 = (P2BodyDist X = [0,100])

;-|-AI Super Attempt-|----------------------------------------------

[State -1, Artificial Intelligence]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [50,100])
trigger1 = (p2bodydist X <= 212) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = numhelper(1001) = 0
value = 1000

[State -1, Artificial Intelligence]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [50,100])
trigger1 = (p2bodydist X <= 212) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = numhelper(1101) = 0
value = 1010

[State -1, Artificial Intelligence]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [50,100])
trigger1 = (p2bodydist X <= 212) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = numhelper(1201) = 0
value = 1020

[State -1, Artificial Intelligence]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [50,100])
trigger1 = (p2bodydist X <= 212) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = numhelper(1301) = 0
value = 1030

[State -1]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [0,500])
trigger1 = (p2bodydist x <= 50) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = NumHelper(6001) = 0
triggerall = NumHelper(6101) = 0
value = 6000

[State -1]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [0,500])
trigger1 = (p2bodydist x <= 90) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = NumHelper(6101) = 0
triggerall = NumHelper(6201) = 0
value = 6100

[State -1]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (random = [0,500])
trigger1 = (p2bodydist x <= 60) && (prevstateno != 5120) && (p2movetype != H) && (statetype != A)
triggerall = NumHelper(6101) = 0
triggerall = NumHelper(6201) = 0
value = 6200

;-|-AI Hyper Attempt-|----------------------------------------------

[State -1, Artificial Intelligence]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (p2statetype != L)
trigger1 = (prevstateno != 5120) && (numproj = 0) && (statetype != A)
trigger1 = (power > 1000) && (random = [60,100]) && (statetype != A)
value = 3000

[State -1, Artificial Intelligence]
type = ChangeState
triggerall = (roundstate = 2) && (var(59) != 0)
triggerall = (Ctrl) && (Statetype = S) && (p2statetype != L)
trigger1 = (prevstateno != 5120) && (numproj = 0) && (statetype != A)
trigger1 = (power > 2000) && (random = [60,100]) && (statetype != A)
value = 3010

;-------------------------------------------------------------------

[State -1, AI Helper Check]
type = ChangeState
trigger1 = IsHelper(9741)
value = 9741

[State -1, AI Helper Check 2]
type = ChangeState
trigger1 = IsHelper(9742)
value = 9742

[State -1, Combo condition Reset]
type = VarSet
trigger1 = 1
var(1) = 0

[State -1, Combo condition Check]
type = VarSet
trigger1 = statetype != A
trigger1 = ctrl
trigger2 = (stateno = [200,299]) || (stateno = [400,499])
trigger2 = stateno != 440 ;Except for sweep kick
trigger2 = movecontact
var(1) = 1
;---------------------------------------------------------------------------
;Special1
;カンフー突き手（強）
[State -1, Special1]
type = ChangeState
value = 1000
triggerall = command = "Special1"
trigger1 = var(1) ;Use combo condition (above)

;---------------------------------------------------------------------------
;Hyper1
[State -1, クッパブレス]
type = ChangeState
value = 3000
triggerall = Command = "Hyper1"
triggerall = power>=1000
trigger1 = StateType != A
trigger1 = Ctrl
triggerall = numhelper = 0

;---------------------------------------------------------------------------
;Hyper2
[State -1, クッパブレス]
type = ChangeState
value = 3010
triggerall = Command = "Hyper2"
triggerall = power>=2000
trigger1 = StateType != A
trigger1 = Ctrl
triggerall = numhelper = 0
;---------------------------------------------------------------------------
;Special1
;カンフー突き手（強）
[State -1, Special1]
type = ChangeState
value = 1010
triggerall = command = "SSpecial1"
trigger1 = var(1) ;Use combo condition (above)

;---------------------------------------------------------------------------
;Special2
;カンフー突き手（強）
[State -1, Special1]
type = ChangeState
value = 1020
triggerall = command = "Special2"
trigger1 = var(1) ;Use combo condition (above)

[State -1, Special1 (air)]
type = ChangeState
value = 1021
triggerall = command = "Special2"
trigger1 = ctrl
trigger2 = (stateno = 600) && (movecontact) && time > 2
trigger3 = (stateno = 610) && (movecontact) && time > 2
trigger4 = (stateno = 620) && (movecontact) && time > 2

;---------------------------------------------------------------------------
;Special2
;カンフー突き手（強）
[State -1, Special2]
type = ChangeState
value = 1030
triggerall = command = "SSpecial2"
trigger1 = var(1) ;Use combo condition (above)
;---------------------------------------------------------------------------
; Throw
[State -1, Throw]
type = ChangeState
value = 800
triggerall = command = "b" || command = "c"
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
trigger1 = command = "holdfwd"
trigger1 = p2bodydist X < 10
trigger1 = (p2statetype = S) || (p2statetype = C)
trigger1 = p2movetype != H
trigger2 = command = "holdback"
trigger2 = p2bodydist X < 10
trigger2 = (p2statetype = S) || (p2statetype = C)
trigger2 = p2movetype != H

;---------------------------------------------------------------------------
; Throw
[State -1, Throw]
type = ChangeState
value = 800
triggerall = command = "y" || command = "z"
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
trigger1 = command = "holdfwd"
trigger1 = p2bodydist X < 10
trigger1 = (p2statetype = S) || (p2statetype = C)
trigger1 = p2movetype != H
trigger2 = command = "holdback"
trigger2 = p2bodydist X < 10
trigger2 = (p2statetype = S) || (p2statetype = C)
trigger2 = p2movetype != H
;-------------------------------------------------------------------------------
;Helpers

[State -1, Patrick]
type = ChangeState
value = 6000
triggerall = command = "Helper1"
trigger1 = statetype != A
trigger1 = ctrl = 1
trigger1 = (statetype = s) && ctrl
trigger2 = (stateno = 200) && movecontact && time > 2
trigger3 = (stateno = 210) && movecontact && time > 2
trigger4 = (stateno = 220) && movecontact && time > 2
trigger5 = (stateno = 230) && movecontact && time > 2
trigger6 = (stateno = 240) && movecontact && time > 2
trigger7 = (stateno = 250) && movecontact && time > 2
trigger8 = (stateno = 400) && movecontact && time > 2
trigger9 = (stateno = 410) && movecontact && time > 2
trigger10 = (stateno = 420) && movecontact && time > 2
trigger11 = (stateno = 430) && movecontact && time > 2
trigger12 = (stateno = 440) && movecontact && time > 2
trigger13 = (stateno = 450) && movecontact && time > 2
trigger10 = var(59) = 1
trigger10 = random > 979
triggerall = NumHelper(6101) = 0

[State -1, Sandy]
type = ChangeState
value = 6100
triggerall = command = "Helper2"
trigger1 = statetype != A
trigger1 = ctrl = 1
trigger1 = (statetype = s) && ctrl
trigger2 = (stateno = 200) && movecontact && time > 2
trigger3 = (stateno = 210) && movecontact && time > 2
trigger4 = (stateno = 220) && movecontact && time > 2
trigger5 = (stateno = 230) && movecontact && time > 2
trigger6 = (stateno = 240) && movecontact && time > 2
trigger7 = (stateno = 250) && movecontact && time > 2
trigger8 = (stateno = 400) && movecontact && time > 2
trigger9 = (stateno = 410) && movecontact && time > 2
trigger10 = (stateno = 420) && movecontact && time > 2
trigger11 = (stateno = 430) && movecontact && time > 2
trigger12 = (stateno = 440) && movecontact && time > 2
trigger13 = (stateno = 450) && movecontact && time > 2
trigger10 = var(59) = 1
trigger10 = random > 979
triggerall = NumHelper(6101) = 0

[State -1, Woody]
type = ChangeState
value = 6200
triggerall = command = "Helper3"
trigger1 = statetype != A
trigger1 = ctrl = 1
trigger1 = (statetype = s) && ctrl
trigger2 = (stateno = 200) && movecontact && time > 2
trigger3 = (stateno = 210) && movecontact && time > 2
trigger4 = (stateno = 220) && movecontact && time > 2
trigger5 = (stateno = 230) && movecontact && time > 2
trigger6 = (stateno = 240) && movecontact && time > 2
trigger7 = (stateno = 250) && movecontact && time > 2
trigger8 = (stateno = 400) && movecontact && time > 2
trigger9 = (stateno = 410) && movecontact && time > 2
trigger10 = (stateno = 420) && movecontact && time > 2
trigger11 = (stateno = 430) && movecontact && time > 2
trigger12 = (stateno = 440) && movecontact && time > 2
trigger13 = (stateno = 450) && movecontact && time > 2
trigger10 = var(59) = 1
trigger10 = random > 979
triggerall = NumHelper(6101) = 0

;===========================================================================
;---------------------------------------------------------------------------
; Run Fwd
[State -1, Run Fwd]
type = ChangeState
value = 100
trigger1 = command = "FF"
trigger1 = statetype = S
trigger1 = ctrl

;---------------------------------------------------------------------------
; Run Back
[State -1, Run Back]
type = ChangeState
value = 105
trigger1 = command = "BB"
trigger1 = statetype = S
trigger1 = ctrl

;===========================================================================
;---------------------------------------------------------------------------
; Taunt
[State -1, Taunt]
type = ChangeState
value = 195
triggerall = command = "s"
trigger1 = statetype != A
trigger1 = ctrl

;---------------------------------------------------------------------------
;Super Jump Up
[State -1, Super Jump Up]
type = ChangeState
value = 60
triggerall = var(59) <= 0
triggerall = command = "super_jump_up" && ctrl
trigger1 = statetype = S && statetype != A 
trigger2 = stateno = 10  
;-----------------------------
;Launcher
[State -1, Launcher] ;by GGN
type = ChangeState
value = 60
triggerall = var(59) <= 0
triggerall = Command = "holdup"
trigger1 = stateno = 420 && movehit

;---------------------------------------------------------------------------
; Stand Light Punch
[State -1, Stand Light Punch]
type = ChangeState
value = 200
triggerall = command = "x"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = 200 && time >= 4

;---------------------------------------------------------------------------
; Stand Medium Punch
[State -1, Stand Medium Punch]
type = ChangeState
value = 210
triggerall = command = "y"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 200

;---------------------------------------------------------------------------
; Stand Strong Punch
[State -1, Stand Strong Punch]
type = ChangeState
value = 220
triggerall = command = "z"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 200
trigger3 = movecontact
trigger3 = stateno = 210

;---------------------------------------------------------------------------
; Stand Light Kick
[State -1, Stand Light Kick]
type = ChangeState
value = 230
triggerall = command = "a"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = 230 && time >= 4


;---------------------------------------------------------------------------
; Stand Medium Kick
[State -1, Stand Medium Kick]
type = ChangeState
value = 240
triggerall = command = "b"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 230

;---------------------------------------------------------------------------
; Stand Strong Kick
[State -1, Stand Strong Kick]
type = ChangeState
value = 250
triggerall = command = "c"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 230
trigger3 = movecontact
trigger3 = stateno = 240

;---------------------------------------------------------------------------
; Crouching Light Punch
[State -1, Crouching Light Punch]
type = ChangeState
value = 400
triggerall = command = "x"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = stateno = 400 && time >= 4

;---------------------------------------------------------------------------
; Crouching Medium Punch
[State -1, Crouching Medium Punch]
type = ChangeState
value = 410
triggerall = command = "y"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 400

;---------------------------------------------------------------------------
; Crouching Strong Punch
[State -1, Crouching Strong Punch]
type = ChangeState
value = 420
triggerall = command = "z"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 400
trigger3 = movecontact
trigger3 = stateno = 410

;---------------------------------------------------------------------------
; Crouching Light Kick
[State -1, Crouching Light Kick]
type = ChangeState
value = 430
triggerall = command = "a"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = stateno = 430 && time >= 4

;---------------------------------------------------------------------------
; Crouching Medium Kick
[State -1, Crouching Medium Kick]
type = ChangeState
value = 440
triggerall = command = "b"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 430

;---------------------------------------------------------------------------
; Crouching Strong Kick
[State -1, Crouching Strong Kick]
type = ChangeState
value = 450
triggerall = command = "c"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 430
trigger3 = movecontact
trigger3 = stateno = 440

;---------------------------------------------------------------------------
; Jump Light Punch
[State -1, Jump Light Punch]
type = ChangeState
value = 600
triggerall = command = "x"
trigger1 = statetype = A
trigger1 = ctrl

;---------------------------------------------------------------------------
; Jump Medium Punch
[State -1, Jump Medium Punch]
type = ChangeState
value = 610
triggerall = command = "y"
trigger1 = statetype = A
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 600

;---------------------------------------------------------------------------
; Jump Strong Punch
[State -1, Jump Strong Punch]
type = ChangeState
value = 620
triggerall = command = "z"
trigger1 = statetype = A
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 600
trigger3 = movecontact
trigger3 = stateno = 610

;---------------------------------------------------------------------------
; Jump Light Kick
[State -1, Jump Light Kick]
type = ChangeState
value = 630
triggerall = command = "a"
trigger1 = statetype = A
trigger1 = ctrl

;---------------------------------------------------------------------------
; Jump Medium Kick
[State -1, Jump Medium Kick]
type = ChangeState
value = 640
triggerall = command = "b"
trigger1 = statetype = A
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 630

;---------------------------------------------------------------------------
; Jump Strong Kick
[State -1, Jump Strong Kick]
type = ChangeState
value = 650
triggerall = command = "c"
trigger1 = statetype = A
trigger1 = ctrl
trigger2 = movecontact
trigger2 = stateno = 630
trigger3 = movecontact
trigger3 = stateno = 640