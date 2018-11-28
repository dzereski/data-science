/* Welcome to the SQL mini project. For this project, you will use
Springboard' online SQL platform, which you can log into through the
following link:

https://sql.springboard.com/
Username: student
Password: learn_sql@springboard

The data you need is in the "country_club" database. This database
contains 3 tables:
    i) the "Bookings" table,
    ii) the "Facilities" table, and
    iii) the "Members" table.

Note that, if you need to, you can also download these tables locally.

In the mini project, you'll be asked a series of questions. You can
solve them using the platform, but for the final deliverable,
paste the code for each solution into this script, and upload it
to your GitHub.

Before starting with the questions, feel free to take your time,
exploring the data, and getting acquainted with the 3 tables. */

/* PRE-WORK:
I run a local instal of MySQL on my mac so I went ahead and installed
a copy of the database locally.  I also connected Jupyter Notebook
to MySQL.  See commits of both the SQL and Jupyter Notebook.  I completed
the mini-project using both the SQL command line tool and Jupyter.

mysql> describe facilities;
+--------------------+--------------+------+-----+---------+-------+
| Field              | Type         | Null | Key | Default | Extra |
+--------------------+--------------+------+-----+---------+-------+
| facid              | int(1)       | NO   | PRI | 0       |       |
| name               | varchar(15)  | YES  |     | NULL    |       |
| membercost         | decimal(2,1) | YES  |     | NULL    |       |
| guestcost          | decimal(3,1) | YES  |     | NULL    |       |
| initialoutlay      | int(5)       | YES  |     | NULL    |       |
| monthlymaintenance | int(4)       | YES  |     | NULL    |       |
+--------------------+--------------+------+-----+---------+-------+
6 rows in set (0.00 sec)

mysql> describe members;
+---------------+-------------+------+-----+---------+-------+
| Field         | Type        | Null | Key | Default | Extra |
+---------------+-------------+------+-----+---------+-------+
| memid         | int(2)      | NO   | PRI | 0       |       |
| surname       | varchar(17) | YES  |     | NULL    |       |
| firstname     | varchar(9)  | YES  |     | NULL    |       |
| address       | varchar(39) | YES  |     | NULL    |       |
| zipcode       | int(5)      | YES  |     | NULL    |       |
| telephone     | varchar(14) | YES  |     | NULL    |       |
| recommendedby | varchar(2)  | YES  |     | NULL    |       |
| joindate      | varchar(19) | YES  |     | NULL    |       |
+---------------+-------------+------+-----+---------+-------+
8 rows in set (0.00 sec)

mysql>
*/

/* Q1: Some of the facilities charge a fee to members, but some do not.
Please list the names of the facilities that do. */

SELECT name FROM facilities WHERE membercost > 0;

/*
+----------------+
| name           |
+----------------+
| Tennis Court 1 |
| Tennis Court 2 |
| Massage Room 1 |
| Massage Room 2 |
| Squash Court   |
+----------------+
5 rows in set (0.00 sec)
*/


/* Q2: How many facilities do not charge a fee to members? */

SELECT count(*) FROM facilities WHERE membercost = 0;

/*
+----------+
| count(*) |
+----------+
|        4 |
+----------+
1 row in set (0.00 sec)
*/


/* Q3: How can you produce a list of facilities that charge a fee to members,
where the fee is less than 20% of the facility's monthly maintenance cost?
Return the facid, facility name, member cost, and monthly maintenance of the
facilities in question. */

SELECT facid, name, membercost, monthlymaintenance
FROM facilities
WHERE membercost > 0 AND (membercost/monthlymaintenance)*100 < 20 ORDER BY membercost DESC;

/*
+-------+----------------+------------+--------------------+
| facid | name           | membercost | monthlymaintenance |
+-------+----------------+------------+--------------------+
|     4 | Massage Room 1 |        9.9 |               3000 |
|     5 | Massage Room 2 |        9.9 |               3000 |
|     0 | Tennis Court 1 |        5.0 |                200 |
|     1 | Tennis Court 2 |        5.0 |                200 |
|     6 | Squash Court   |        3.5 |                 80 |
+-------+----------------+------------+--------------------+
5 rows in set (0.00 sec)
*/


/* Q4: How can you retrieve the details of facilities with ID 1 and 5?
Write the query without using the OR operator. */

SELECT * FROM facilities WHERE facid IN (1, 5);

/*
+-------+----------------+------------+-----------+---------------+--------------------+
| facid | name           | membercost | guestcost | initialoutlay | monthlymaintenance |
+-------+----------------+------------+-----------+---------------+--------------------+
|     1 | Tennis Court 2 |        5.0 |      25.0 |          8000 |                200 |
|     5 | Massage Room 2 |        9.9 |      80.0 |          4000 |               3000 |
+-------+----------------+------------+-----------+---------------+--------------------+
2 rows in set (0.00 sec)
*/


/* Q5: How can you produce a list of facilities, with each labelled as
'cheap' or 'expensive', depending on if their monthly maintenance cost is
more than $100? Return the name and monthly maintenance of the facilities
in question. */

SELECT
    name,
    monthlymaintenance,
    CASE
        WHEN monthlymaintenance > 100 THEN 'expensive'
        ELSE 'cheap'
    END as facility_label
FROM facilities
ORDER BY monthlymaintenance DESC;

/*
+-----------------+--------------------+----------------+
| name            | monthlymaintenance | facility_label |
+-----------------+--------------------+----------------+
| Massage Room 1  |               3000 | expensive      |
| Massage Room 2  |               3000 | expensive      |
| Tennis Court 1  |                200 | expensive      |
| Tennis Court 2  |                200 | expensive      |
| Squash Court    |                 80 | cheap          |
| Badminton Court |                 50 | cheap          |
| Snooker Table   |                 15 | cheap          |
| Pool Table      |                 15 | cheap          |
| Table Tennis    |                 10 | cheap          |
+-----------------+--------------------+----------------+
9 rows in set (0.00 sec)
*/


/* Q6: You'd like to get the first and last name of the last member(s)
who signed up. Do not use the LIMIT clause for your solution. */

SELECT memid, firstname, surname FROM members WHERE memid = (SELECT MAX(memid) FROM members);

/*
+-------+-----------+---------+
| memid | firstname | surname |
+-------+-----------+---------+
|    37 | Darren    | Smith   |
+-------+-----------+---------+
1 row in set (0.00 sec)
*/


/* Q7: How can you produce a list of all members who have used a tennis court?
Include in your output the name of the court, and the name of the member
formatted as a single column. Ensure no duplicate data, and order by
the member name. */

SELECT
    DISTINCT members.memid,
    CONCAT(surname, ', ', firstname) as member_name,
    name as court_name
FROM Bookings JOIN Members ON bookings.memid=members.memid JOIN Facilities ON bookings.facid=facilities.facid
WHERE name like 'Tennis%' AND members.memid > 0
ORDER BY member_name;

/*
+-------+--------------------+----------------+
| memid | member_name        | court_name     |
+-------+--------------------+----------------+
|    15 | Bader, Florence    | Tennis Court 2 |
|    15 | Bader, Florence    | Tennis Court 1 |
|    12 | Baker, Anne        | Tennis Court 1 |
|    12 | Baker, Anne        | Tennis Court 2 |
|    16 | Baker, Timothy     | Tennis Court 2 |
|    16 | Baker, Timothy     | Tennis Court 1 |
|     8 | Boothe, Tim        | Tennis Court 2 |
|     8 | Boothe, Tim        | Tennis Court 1 |
|     5 | Butters, Gerald    | Tennis Court 2 |
|     5 | Butters, Gerald    | Tennis Court 1 |
|    22 | Coplin, Joan       | Tennis Court 1 |
|    36 | Crumpet, Erica     | Tennis Court 1 |
|     7 | Dare, Nancy        | Tennis Court 2 |
|     7 | Dare, Nancy        | Tennis Court 1 |
|    28 | Farrell, David     | Tennis Court 2 |
|    28 | Farrell, David     | Tennis Court 1 |
|    13 | Farrell, Jemima    | Tennis Court 1 |
|    13 | Farrell, Jemima    | Tennis Court 2 |
|    20 | Genting, Matthew   | Tennis Court 1 |
|    35 | Hunt, John         | Tennis Court 1 |
|    35 | Hunt, John         | Tennis Court 2 |
|    11 | Jones, David       | Tennis Court 2 |
|    11 | Jones, David       | Tennis Court 1 |
|    26 | Jones, Douglas     | Tennis Court 1 |
|     4 | Joplette, Janice   | Tennis Court 1 |
|     4 | Joplette, Janice   | Tennis Court 2 |
|    10 | Owen, Charles      | Tennis Court 1 |
|    10 | Owen, Charles      | Tennis Court 2 |
|    17 | Pinker, David      | Tennis Court 1 |
|    30 | Purview, Millicent | Tennis Court 2 |
|     3 | Rownam, Tim        | Tennis Court 2 |
|     3 | Rownam, Tim        | Tennis Court 1 |
|    27 | Rumney, Henrietta  | Tennis Court 2 |
|    24 | Sarwin, Ramnaresh  | Tennis Court 1 |
|    24 | Sarwin, Ramnaresh  | Tennis Court 2 |
|     1 | Smith, Darren      | Tennis Court 2 |
|    14 | Smith, Jack        | Tennis Court 2 |
|    14 | Smith, Jack        | Tennis Court 1 |
|     2 | Smith, Tracy       | Tennis Court 2 |
|     2 | Smith, Tracy       | Tennis Court 1 |
|     9 | Stibbons, Ponder   | Tennis Court 2 |
|     9 | Stibbons, Ponder   | Tennis Court 1 |
|     6 | Tracy, Burton      | Tennis Court 2 |
|     6 | Tracy, Burton      | Tennis Court 1 |
+-------+--------------------+----------------+
44 rows in set (0.00 sec)
*/


/* Q8: How can you produce a list of bookings on the day of 2012-09-14 which
will cost the member (or guest) more than $30? Remember that guests have
different costs to members (the listed costs are per half-hour 'slot'), and
the guest user's ID is always 0. Include in your output the name of the
facility, the name of the member formatted as a single column, and the cost.
Order by descending cost, and do not use any subqueries. */

SELECT
    DATE(starttime) AS date,
    bookid,
    CASE
        WHEN Members.memid=0 THEN 'GUEST'
        ELSE concat(surname, ', ', firstname)
    END AS user_name,
    name as facility_name,
    slots,
    CASE
        WHEN Members.memid=0 THEN guestcost*slots
        ELSE membercost*slots
    END AS booking_cost
FROM Bookings JOIN Members ON Bookings.memid=Members.memid JOIN Facilities ON Bookings.facid=Facilities.facid
WHERE
    DATE(starttime)='2012-09-14'
HAVING booking_cost > 30
ORDER BY booking_cost DESC;

/*
+------------+--------+-----------------+----------------+-------+--------------+
| date       | bookid | user_name       | facility_name  | slots | booking_cost |
+------------+--------+-----------------+----------------+-------+--------------+
| 2012-09-14 |   2946 | GUEST           | Massage Room 2 |     4 |        320.0 |
| 2012-09-14 |   2937 | GUEST           | Massage Room 1 |     2 |        160.0 |
| 2012-09-14 |   2940 | GUEST           | Massage Room 1 |     2 |        160.0 |
| 2012-09-14 |   2942 | GUEST           | Massage Room 1 |     2 |        160.0 |
| 2012-09-14 |   2926 | GUEST           | Tennis Court 2 |     6 |        150.0 |
| 2012-09-14 |   2920 | GUEST           | Tennis Court 1 |     3 |         75.0 |
| 2012-09-14 |   2922 | GUEST           | Tennis Court 1 |     3 |         75.0 |
| 2012-09-14 |   2925 | GUEST           | Tennis Court 2 |     3 |         75.0 |
| 2012-09-14 |   2948 | GUEST           | Squash Court   |     4 |         70.0 |
| 2012-09-14 |   2941 | Farrell, Jemima | Massage Room 1 |     4 |         39.6 |
| 2012-09-14 |   2949 | GUEST           | Squash Court   |     2 |         35.0 |
| 2012-09-14 |   2951 | GUEST           | Squash Court   |     2 |         35.0 |
+------------+--------+-----------------+----------------+-------+--------------+
12 rows in set (0.00 sec)
*/


/* Q9: This time, produce the same result as in Q8, but using a subquery. */

SELECT
    DATE(starttime) AS date,
    bookid,
    CASE
        WHEN memid=0 THEN 'GUEST'
        ELSE concat(surname, ', ', firstname)
    END AS user_name,
    facility_name,
    slots,
    CASE
        WHEN memid=0 THEN guestcost*slots
        ELSE membercost*slots
    END AS booking_cost
FROM
    (SELECT bookid, members.memid, firstname, surname, slots, guestcost, membercost, starttime, name as facility_name
     FROM Bookings JOIN Members ON Bookings.memid=Members.memid JOIN Facilities ON Bookings.facid=Facilities.facid
     WHERE DATE(starttime)='2012-09-14') AS day_bookings
HAVING booking_cost > 30
ORDER BY booking_cost DESC;

/*
+------------+--------+-----------------+----------------+-------+--------------+
| date       | bookid | user_name       | facility_name  | slots | booking_cost |
+------------+--------+-----------------+----------------+-------+--------------+
| 2012-09-14 |   2946 | GUEST           | Massage Room 2 |     4 |        320.0 |
| 2012-09-14 |   2937 | GUEST           | Massage Room 1 |     2 |        160.0 |
| 2012-09-14 |   2940 | GUEST           | Massage Room 1 |     2 |        160.0 |
| 2012-09-14 |   2942 | GUEST           | Massage Room 1 |     2 |        160.0 |
| 2012-09-14 |   2926 | GUEST           | Tennis Court 2 |     6 |        150.0 |
| 2012-09-14 |   2920 | GUEST           | Tennis Court 1 |     3 |         75.0 |
| 2012-09-14 |   2922 | GUEST           | Tennis Court 1 |     3 |         75.0 |
| 2012-09-14 |   2925 | GUEST           | Tennis Court 2 |     3 |         75.0 |
| 2012-09-14 |   2948 | GUEST           | Squash Court   |     4 |         70.0 |
| 2012-09-14 |   2941 | Farrell, Jemima | Massage Room 1 |     4 |         39.6 |
| 2012-09-14 |   2949 | GUEST           | Squash Court   |     2 |         35.0 |
| 2012-09-14 |   2951 | GUEST           | Squash Court   |     2 |         35.0 |
+------------+--------+-----------------+----------------+-------+--------------+
12 rows in set (0.01 sec)
*/


/* Q10: Produce a list of facilities with a total revenue less than 1000.
The output of facility name and total revenue, sorted by revenue. Remember
that there's a different cost for guests and members! */

SELECT
    facilities.name,
    SUM(CASE
            WHEN memid=0 THEN guestcost*slots
            ELSE membercost*slots
        END) AS revenue
FROM Bookings JOIN Facilities ON Bookings.facid=Facilities.facid
GROUP BY bookings.facid
HAVING revenue < 1000
ORDER BY revenue DESC;

/*
+---------------+---------+
| name          | revenue |
+---------------+---------+
| Pool Table    |   270.0 |
| Snooker Table |   240.0 |
| Table Tennis  |   180.0 |
+---------------+---------+
3 rows in set (0.00 sec)
*/
