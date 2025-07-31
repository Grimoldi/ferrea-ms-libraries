/*
User and role creation, as well as rbac for only required nodes and relationship.

The role will be a copy of the base role editor, which gives the following permissions:
can perform traverse, read, and write operations on all databases except system, but cannot make new labels or relationship types.
*/


// add the following as parameters
/*
:param {
    user: "ferrea_lbs",
    password: "xyz"
}
*/

// create role (unique for each microservices, as the priviliges will be linked to the role)
// for the sake of semplicity, with the same name of the user
CREATE ROLE $user IF NOT EXISTS AS COPY OF editor;

// create the specific user for this microservice, and grant the role previously created
CREATE USER $user IF NOT EXISTS SET PASSWORD $password CHANGE NOT REQUIRED ; 
GRANT ROLE $role TO $user;

// grant the ability to traverse + read all attributes ({*}) to the role (and therefore the user)
GRANT MATCH {*} ON HOME GRAPH NODES Library TO $role;
