INSERT INTO USER (dname, uname) VALUES ('no password', 't1');
-- Test login(t1, *) --> set_pw
INSERT INTO USER (dname, uname, pw_hash) VALUES ('dummy pw', 't2', '$argon2id$v=19$m=65536,t=3,p=4$zB0uhNR7VckqlboXD3Dfkg$/J0g13r8/NqEUOkdcyesG1wJ+N++ekZztmf6uX4omqU');
-- Test login(t2, ) --> error
-- Test login(t2, random) --> error
-- Test login(t2, "dummy") --> set_pw
INSERT INTO USER (dname, uname, pw_hash, dummy_pw) VALUES ('password', 't3', '$argon2id$v=19$m=65536,t=3,p=4$CpZZ2x4LW1BM1Rrdurfqyw$HtOne3SXTOV2rtdxyVuja2QxxoMb8Y7vjxUPNWmOLfg', 0);
-- Test login(t3, ) --> error
-- Test login(t3, random) --> error
-- Test login(t3, "password") --> login_success