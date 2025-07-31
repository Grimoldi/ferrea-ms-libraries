CREATE CONSTRAINT unique_ferrea_id
FOR (l:Library) REQUIRE l.fid IS UNIQUE;