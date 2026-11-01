
































































































































[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s


[Defaults]

command.time = 15



command.buffer.time = 1


[Command]
name = "SuperJump"
command = $D, $U
time = 10

[Command]
name = "FF"
command = F, F
time = 10

[Command]
name = "BB"
command = B, B
time = 10


[Command]
name = "recovery"
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
name = "start"
command = s
time = 1


[Command]
name = "holda"
command = /a
time = 1

[Command]
name = "holdb"
command = /b
time = 1

[Command]
name = "holdc"
command = /c
time = 1

[Command]
name = "holdx"
command = /x
time = 1

[Command]
name = "holdy"
command = /y
time = 1

[Command]
name = "holdz"
command = /z
time = 1

[Command]
name = "holdstart"
command = /s
time = 1


[Command]
name = "holdfwd"
command = /$F
time = 1

[Command]
name = "holdback"
command = /$B
time = 1

[Command]
name = "holdup"
command = /$U
time = 1

[Command]
name = "holddown"
command = /$D
time = 1










































[Statedef -1]

[State -1, Super Jump]
type = ChangeState
value = 60
triggerall = !AIlevel && roundstate =2
triggerall = StateType = S || StateType = C
triggerall = ctrl
trigger1 = command = "SuperJump"
trigger2 = (command = "a" && command = "b") || (command = "b" && command = "c") || (command = "a" && command = "b" && command = "c")





[State -1, Run Forward]
type = ChangeState
value = ifelse(pos y >= 0,100,101)
triggerall = AILevel <= 0
triggerall = roundstate =2
triggerall = (Stateno != [100,199])
triggerall = ctrl
trigger1 = command = "FF"
trigger2 = command = "holdfwd"
trigger2 = (command = "x" && command = "y") || (command = "y" && command = "z") || (command = "x" && command = "y" && command = "z")


[State -1, Run Backward]
type = ChangeState
value = ifelse(pos y >= 0,105,106)
triggerall = AILevel <= 0
triggerall = roundstate =2
triggerall = (Stateno != [100,199])
triggerall = ctrl
trigger1 = command = "BB"
trigger2 = command = "holdback"
trigger2 = (command = "x" && command = "y") || (command = "y" && command = "z") || (command = "x" && command = "y" && command = "z")





[State -1, Taunt]
type = ChangeState
value = 999
triggerall = !AILevel
triggerall = command = "start"
trigger1 = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)









[State -1, Stand Light Punch]
type = ChangeState
value = 200
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "x" && command != "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [300,399]) && movecontact


[State -1, Stand Medium Punch]
type = ChangeState
value = 210
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "y" && command != "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [300,399]) && movecontact
trigger4 = stateno = 200 && movecontact
trigger5 = stateno = 230 && movecontact
trigger6 = stateno = 240 && movecontact


[State -1, Stand Heavy Punch]
type = ChangeState
value = 220
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "z" && command != "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [300,399]) && movecontact
trigger4 = stateno = 200 && movecontact
trigger5 = stateno = 210 && movecontact
trigger6 = stateno = 230 && movecontact
trigger7 = stateno = 240 && movecontact


[State -1, Stand Light Kick]
type = ChangeState
value = 230
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "a" && command != "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [300,399]) && movecontact
trigger4 = stateno = 200 && movecontact
trigger5 = stateno = 210 && movecontact
trigger6 = stateno = 220 && movecontact
trigger7 = stateno = 240 && movecontact
trigger8 = stateno = 250 && movecontact





[State -1, Crouch Light Punch]
type = ChangeState
value = 300
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "x" && command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [200,299]) && movecontact


[State -1, Crouch Medium Punch]
type = ChangeState
value = 310
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "y" && command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [200,299]) && movecontact
trigger4 = stateno = 300 && movecontact
trigger5 = stateno = 330 && movecontact
trigger6 = stateno = 340 && movecontact


[State -1, Crouch Heavy Punch]
type = ChangeState
value = 320
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "z" && command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [200,299]) && movecontact
trigger4 = stateno = 300 && movecontact
trigger5 = stateno = 310 && movecontact
trigger6 = stateno = 330 && movecontact
trigger7 = stateno = 340 && movecontact
trigger8 = stateno = 350 && movecontact


[State -1, Crouch Light Kick]
type = ChangeState
value = 330
triggerall = !AIlevel && roundstate =2
triggerall = command = "a" && command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (Stateno = 100 || Stateno = 105)
trigger3 = (stateno = [200,299]) && movecontact
trigger4 = stateno = 300 && movecontact





[State -1, Air Light Punch]
type = ChangeState
value = 400
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "x" && Statetype = A
trigger1 = ctrl
trigger2 = (Stateno = 101 || Stateno = 106)


[State -1, Air Medium Punch]
type = ChangeState
value = 410
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "y" && Statetype = A
trigger1 = ctrl
trigger2 = (Stateno = 101 || Stateno = 106)
trigger3 = stateno = 400 && movecontact
trigger4 = stateno = 430 && movecontact
trigger5 = stateno = 440 && movecontact


[State -1, Air Heavy Punch]
type = ChangeState
value = 420
triggerall = AILevel <= 0
triggerall = !AIlevel && roundstate =2
triggerall = command = "z" && Statetype = A
trigger1 = ctrl
trigger2 = (Stateno = 101 || Stateno = 106)
trigger3 = stateno = 400 && movecontact
trigger4 = stateno = 410 && movecontact
trigger5 = stateno = 430 && movecontact
trigger6 = stateno = 440 && movecontact

;Air Light Kick
[State -1, Air Light Kick]
type = ChangeState
value = 430
triggerall = !AIlevel && roundstate =2
triggerall = command = "a" && Statetype = A
trigger1 = ctrl
trigger2 = (Stateno = 101 || Stateno = 106)
trigger3 = stateno = 400 && movecontact
