INSERT INTO USER (dname, uname) VALUES ('no password', 't1');

INSERT INTO USER (dname, uname, pw_hash) VALUES ('dummy pw', 't2', '$argon2id$v=19$m=65536,t=3,p=4$zB0uhNR7VckqlboXD3Dfkg$/J0g13r8/NqEUOkdcyesG1wJ+N++ekZztmf6uX4omqU');

INSERT INTO USER (dname, uname, pw_hash) VALUES ('password(dummy)', 't3', '$argon2id$v=19$m=65536,t=3,p=4$CpZZ2x4LW1BM1Rrdurfqyw$HtOne3SXTOV2rtdxyVuja2QxxoMb8Y7vjxUPNWmOLfg');

INSERT INTO USER (dname, uname, pw_hash, dummy_pw) VALUES ('password', 't4', '$argon2id$v=19$m=65536,t=3,p=4$CpZZ2x4LW1BM1Rrdurfqyw$HtOne3SXTOV2rtdxyVuja2QxxoMb8Y7vjxUPNWmOLfg', 0);
-- Must ask for old password

-- TESTS:
-- Must not accept mismatch passwords
-- Must not accept password shorter than 8 chars
-- Must not accept password that is the same as old password (dummy or not)
-- Must set new password for dummy accounts if valid
-- Must not set new password unless correct old pw is given (if not dummy)