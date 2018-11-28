SELECT
    bookings.bookid,
    bookings.facid,
    bookings.memid,
    if(bookings.memid=0, guestcost*slots, membercost*slots) AS booking_cost
FROM Bookings JOIN Members ON Bookings.memid=Members.memid JOIN Facilities ON Bookings.facid=Facilities.facid
HAVING booking_cost > 0
ORDER BY booking_cost DESC;
