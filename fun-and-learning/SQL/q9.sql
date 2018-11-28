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
