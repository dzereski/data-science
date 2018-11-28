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