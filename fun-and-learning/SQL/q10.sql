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
