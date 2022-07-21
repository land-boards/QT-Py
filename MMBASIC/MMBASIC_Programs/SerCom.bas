' SerCom.bas - Use the Serial port as a COM port
SetPin gp1,gp0, com1
Open "com1:9600" As #5
Print #5, "Hello, World!"
dat$ = Input$(20, #5)
Print dat$
Close #5
